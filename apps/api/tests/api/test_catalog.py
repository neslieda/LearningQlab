"""GET /v1/programs and `syllabus.list_catalog`: the subjects questions can be written against."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from qlab.organizations.service import Role
from qlab.syllabus.service import list_catalog, load_reference
from tests.api.support import ApiHarness
from tests.syllabus.test_syllabus_service import make_reference

pytestmark = pytest.mark.db

COUNT_ALL = (
    "SELECT (SELECT count(*) FROM program) + (SELECT count(*) FROM subject) "
    "+ (SELECT count(*) FROM syllabus_version) + (SELECT count(*) FROM syllabus_node) "
    "+ (SELECT count(*) FROM exam_format)"
)


def load(session: Session, program: str, subject: str, version: str) -> None:
    load_reference(
        session,
        make_reference(
            program=program,
            program_name=f"Name of {program}",
            subject=subject,
            subject_name=f"Name of {subject}",
            version=version,
            version_title=f"Title of {version}",
        ),
    )


def add_version_without_format(session: Session, program: str, subject: str, code: str) -> None:
    session.execute(
        text(
            "INSERT INTO syllabus_version (id, subject_id, code, title, status) "
            "SELECT :id, s.id, :code, :title, 'synthetic' FROM subject s "
            "JOIN program p ON p.id = s.program_id WHERE p.code = :p AND s.code = :s"
        ),
        {"id": uuid.uuid7(), "code": code, "title": f"Title of {code}", "p": program, "s": subject},
    )
    session.flush()


def get(api: ApiHarness, *roles: Role) -> dict:  # type: ignore[type-arg]
    response = api.client.get("/v1/programs", headers=api.headers(*roles))
    assert response.status_code == 200, response.text
    return response.json()  # type: ignore[no-any-return]


def test_empty_database_gives_no_items(api: ApiHarness, session: Session) -> None:
    assert list_catalog(session) == []
    assert get(api, Role.STUDENT) == {"items": []}


def test_items_are_ordered_by_programme_then_subject_code(
    api: ApiHarness, session: Session
) -> None:
    load(session, "pb", "z_sub", "v1")
    load(session, "pa", "b_sub", "v1")
    load(session, "pb", "a_sub", "v1")
    load(session, "pa", "a_sub", "v1")
    body = get(api, Role.STUDENT)
    assert [(i["program"], i["subject"]) for i in body["items"]] == [
        ("pa", "a_sub"),
        ("pa", "b_sub"),
        ("pb", "a_sub"),
        ("pb", "z_sub"),
    ]


def test_versions_are_newest_first(api: ApiHarness, session: Session) -> None:
    for version in ("v1", "v2", "v3"):
        load(session, "pa", "sub", version)
    body = get(api, Role.STUDENT)
    assert len(body["items"]) == 1
    assert [v["code"] for v in body["items"][0]["versions"]] == ["v3", "v2", "v1"]


def test_response_shape(api: ApiHarness, session: Session) -> None:
    load(session, "pa", "sub", "v1")
    assert get(api, Role.STUDENT) == {
        "items": [
            {
                "program": "pa",
                "program_name": "Name of pa",
                "subject": "sub",
                "subject_name": "Name of sub",
                "versions": [{"code": "v1", "title": "Title of v1"}],
            }
        ]
    }


def test_a_version_without_exam_format_is_excluded(api: ApiHarness, session: Session) -> None:
    load(session, "pa", "sub", "v1")
    add_version_without_format(session, "pa", "sub", "v2")
    body = get(api, Role.STUDENT)
    assert [v["code"] for v in body["items"][0]["versions"]] == ["v1"]
    assert list_catalog(session)[0].versions == (("v1", "Title of v1"),)


def test_a_subject_with_only_versions_lacking_exam_format_is_excluded(
    api: ApiHarness, session: Session
) -> None:
    load(session, "pa", "kept", "v1")
    load(session, "pa", "dropped", "v1")
    session.execute(
        text(
            "DELETE FROM exam_format WHERE syllabus_version_id IN (SELECT v.id FROM "
            "syllabus_version v JOIN subject s ON s.id = v.subject_id WHERE s.code = 'dropped')"
        )
    )
    add_version_without_format(session, "pa", "dropped", "v2")
    body = get(api, Role.STUDENT)
    assert [i["subject"] for i in body["items"]] == ["kept"]


def test_every_role_sees_the_same_catalog_and_reading_writes_nothing(
    api: ApiHarness, session: Session
) -> None:
    load(session, "pa", "sub", "v1")
    before = session.execute(text(COUNT_ALL)).scalar_one()
    bodies = [get(api, role) for role in Role]
    assert all(b == bodies[0] for b in bodies)
    assert get(api, Role.STUDENT) == bodies[0]
    assert session.execute(text(COUNT_ALL)).scalar_one() == before


def test_no_token_is_unauthenticated(api: ApiHarness) -> None:
    assert api.client.get("/v1/programs").status_code == 401
