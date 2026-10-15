"""The syllabus tree: `syllabus.get_tree` and the syllabus endpoint
(`GET /v1/programs/{program}/subjects/{subject}/syllabus`; docs/slices/M1G-5-SOZLESME.md
sections 2 and 3.6; docs/slices/M1G-5-YETKILER.md section 1, row 3).
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

import pytest
from sqlalchemy import Connection, text
from sqlalchemy.orm import Session

from qlab.api.schemas import SyllabusOut
from qlab.organizations.service import Role
from qlab.syllabus.reference import SyllabusReference
from qlab.syllabus.service import SyllabusTree, TreeNode, get_tree, load_reference
from tests.api.support import ALL_ROLES, ApiHarness, make_harness
from tests.conftest import REPO_ROOT

pytestmark = pytest.mark.db

REAL_FILE = REPO_ROOT / "content" / "reference" / "dp-physics-2025-syllabus.json"


# --- reference data ---------------------------------------------------------------------------


def real_reference() -> SyllabusReference:
    return SyllabusReference.model_validate_json(REAL_FILE.read_bytes())


def reference(
    *,
    program: str = "demo",
    subject: str = "sub",
    version: str = "v1",
    version_title: str = "Version one",
    status: str = "synthetic test data",
    nodes: list[dict[str, Any]] | None = None,
    sections: list[tuple[str, str]] | None = None,
    command_terms: list[str] | None = None,
) -> SyllabusReference:
    default_nodes: list[dict[str, Any]] = [
        {"code": "X", "title": "Top X"},
        {"code": "X.1", "title": "First", "parent": "X", "attributes": {"level": "core"}},
        {"code": "X.2", "title": "Second", "parent": "X"},
        {"code": "Y", "title": "Top Y"},
        {"code": "Y.1", "title": "Third", "parent": "Y"},
        {"code": "Y.1.a", "title": "Deep", "parent": "Y.1", "attributes": {"k": "v"}},
    ]
    return SyllabusReference.model_validate(
        {
            "status": status,
            "program": {"code": program, "name": f"Programme {program}"},
            "subject": {"code": subject, "name": f"Subject {subject}"},
            "syllabus_version": {"code": version, "title": version_title},
            "nodes": nodes if nodes is not None else default_nodes,
            "exam_format": {
                "code": "main",
                "sections": [
                    {"code": code, "title": title}
                    for code, title in (sections or [("s2", "Second paper"), ("s1", "First paper")])
                ],
                "command_terms": command_terms or ["zeta", "alpha", "mu"],
            },
        }
    )


def leaf_codes(ref: SyllabusReference) -> frozenset[str]:
    parents = {n.parent for n in ref.nodes if n.parent is not None}
    return frozenset(n.code for n in ref.nodes if n.code not in parents)


def tree_of(session: Session, ref: SyllabusReference, version: str | None = None) -> SyllabusTree:
    tree = get_tree(session, program=ref.program.code, subject=ref.subject.code, version=version)
    assert tree is not None
    return tree


def table_sizes(connection: Connection) -> dict[str, int]:
    names = [
        row[0]
        for row in connection.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY 1")
        )
    ]
    return {
        name: int(connection.execute(text(f'SELECT count(*) FROM "{name}"')).scalar_one())  # noqa: S608
        for name in names
    }


# =============================================================================================
# get_tree
# =============================================================================================


def test_tree_carries_the_codes_titles_and_status_of_the_version(session: Session) -> None:
    ref = reference(version_title="A fine title", status="draft: waiting for an expert")
    load_reference(session, ref)

    tree = tree_of(session, ref)

    assert isinstance(tree, SyllabusTree)
    assert (tree.program, tree.subject, tree.version) == ("demo", "sub", "v1")
    assert tree.title == "A fine title"
    assert tree.status == "draft: waiting for an expert"


def test_nodes_come_in_syllabus_order_with_parents_before_children(session: Session) -> None:
    ref = reference()
    load_reference(session, ref)

    tree = tree_of(session, ref)

    assert [n.code for n in tree.nodes] == [n.code for n in ref.nodes]
    position = {n.code: i for i, n in enumerate(tree.nodes)}
    for node in tree.nodes:
        if node.parent is not None:
            assert position[node.parent] < position[node.code]


def test_node_fields(session: Session) -> None:
    ref = reference()
    load_reference(session, ref)

    nodes = {n.code: n for n in tree_of(session, ref).nodes}

    assert all(isinstance(n, TreeNode) for n in nodes.values())
    assert nodes["X"].parent is None
    assert nodes["X"].title == "Top X"
    assert nodes["X.1"].parent == "X"
    assert nodes["X.1"].attributes == {"level": "core"}
    assert nodes["X.2"].attributes == {}
    assert nodes["Y.1.a"].parent == "Y.1"
    assert nodes["Y.1.a"].attributes == {"k": "v"}


def test_is_leaf_is_true_exactly_for_nodes_without_children(session: Session) -> None:
    ref = reference()
    load_reference(session, ref)

    nodes = {n.code: n for n in tree_of(session, ref).nodes}

    assert {code for code, n in nodes.items() if n.is_leaf} == {"X.1", "X.2", "Y.1.a"}
    assert not nodes["X"].is_leaf
    assert not nodes["Y.1"].is_leaf


def test_a_single_top_level_node_without_children_is_a_leaf(session: Session) -> None:
    ref = reference(nodes=[{"code": "ONLY", "title": "Only node"}])
    load_reference(session, ref)

    (node,) = tree_of(session, ref).nodes

    assert node.is_leaf is True
    assert node.parent is None


def test_exam_sections_keep_the_order_of_the_exam_format(session: Session) -> None:
    # Declared as s2, s1: not alphabetical, so a sorted result would fail.
    ref = reference(sections=[("s2", "Second paper"), ("s1", "First paper"), ("s0", "Zero paper")])
    load_reference(session, ref)

    tree = tree_of(session, ref)

    assert tree.exam_sections == (
        ("s2", "Second paper"),
        ("s1", "First paper"),
        ("s0", "Zero paper"),
    )


def test_command_terms_are_the_terms_of_the_exam_format(session: Session) -> None:
    ref = reference(command_terms=["zeta", "alpha", "mu"])
    load_reference(session, ref)

    tree = tree_of(session, ref)

    assert isinstance(tree.command_terms, tuple)
    assert sorted(tree.command_terms) == ["alpha", "mu", "zeta"]
    assert len(tree.command_terms) == len(set(tree.command_terms))


def test_the_real_reference_file_round_trips(session: Session) -> None:
    ref = real_reference()
    load_reference(session, ref)

    tree = tree_of(session, ref)

    assert (tree.program, tree.subject, tree.version) == ("ib_dp", "physics", "2025")
    assert tree.title == ref.syllabus_version.title
    assert tree.status == ref.status
    assert [n.code for n in tree.nodes] == [n.code for n in ref.nodes]
    assert {n.code for n in tree.nodes if n.is_leaf} == leaf_codes(ref)
    assert {n.code: n.parent for n in tree.nodes} == {n.code: n.parent for n in ref.nodes}
    assert {n.code: n.title for n in tree.nodes} == {n.code: n.title for n in ref.nodes}
    assert {n.code: n.attributes for n in tree.nodes} == {n.code: n.attributes for n in ref.nodes}
    assert tree.exam_sections == tuple((s.code, s.title) for s in ref.exam_format.sections)
    assert sorted(tree.command_terms) == sorted(ref.exam_format.command_terms)
    position = {n.code: i for i, n in enumerate(tree.nodes)}
    assert all(position[n.parent] < position[n.code] for n in tree.nodes if n.parent)


# --- None cases ---------------------------------------------------------------------------------


def test_unknown_program_is_none(session: Session) -> None:
    load_reference(session, reference())
    assert get_tree(session, program="nope", subject="sub") is None


def test_unknown_subject_is_none(session: Session) -> None:
    load_reference(session, reference())
    assert get_tree(session, program="demo", subject="nope") is None


def test_subject_of_another_program_is_none(session: Session) -> None:
    load_reference(session, reference(program="p1", subject="s1x"))
    load_reference(session, reference(program="p2", subject="s2x"))
    assert get_tree(session, program="p1", subject="s2x") is None
    assert get_tree(session, program="p2", subject="s1x") is None


def test_unknown_version_is_none(session: Session) -> None:
    load_reference(session, reference())
    assert get_tree(session, program="demo", subject="sub", version="v9") is None


def test_nothing_loaded_is_none(session: Session) -> None:
    assert get_tree(session, program="demo", subject="sub") is None
    assert get_tree(session, program="demo", subject="sub", version="v1") is None


def test_empty_codes_are_none(session: Session) -> None:
    load_reference(session, reference())
    assert get_tree(session, program="", subject="sub") is None
    assert get_tree(session, program="demo", subject="") is None
    assert get_tree(session, program="demo", subject="sub", version="") is None


def test_codes_are_matched_exactly(session: Session) -> None:
    load_reference(session, reference())
    assert get_tree(session, program="DEMO", subject="sub") is None
    assert get_tree(session, program="demo", subject="SUB") is None
    assert get_tree(session, program="demo", subject="sub", version="V1") is None
    assert get_tree(session, program="demo%", subject="sub") is None
    assert get_tree(session, program="dem_", subject="sub") is None


def test_a_version_without_an_exam_format_is_none(session: Session, connection: Connection) -> None:
    version_id = load_reference(session, reference())
    connection.execute(
        text("DELETE FROM exam_format WHERE syllabus_version_id = :v"), {"v": version_id}
    )
    session.expire_all()

    assert get_tree(session, program="demo", subject="sub", version="v1") is None
    assert get_tree(session, program="demo", subject="sub") is None


# --- versions -----------------------------------------------------------------------------------


def two_versions(session: Session) -> tuple[SyllabusReference, SyllabusReference]:
    older = reference(
        version="v1",
        version_title="Older",
        nodes=[{"code": "OLD", "title": "Old node"}],
        sections=[("a", "Old section")],
    )
    load_reference(session, older)
    time.sleep(0.02)  # identifiers are time-ordered: keep the second one clearly later
    newer = reference(
        version="v2",
        version_title="Newer",
        nodes=[
            {"code": "NEW", "title": "New node"},
            {"code": "NEW.1", "title": "n", "parent": "NEW"},
        ],
        sections=[("b", "New section")],
    )
    load_reference(session, newer)
    return older, newer


def test_without_a_version_the_newest_one_is_returned(session: Session) -> None:
    two_versions(session)

    tree = get_tree(session, program="demo", subject="sub")

    assert tree is not None
    assert tree.version == "v2"
    assert tree.title == "Newer"
    assert [n.code for n in tree.nodes] == ["NEW", "NEW.1"]
    assert tree.exam_sections == (("b", "New section"),)


def test_an_explicit_older_version_is_returned_as_asked(session: Session) -> None:
    two_versions(session)

    tree = get_tree(session, program="demo", subject="sub", version="v1")

    assert tree is not None
    assert tree.version == "v1"
    assert tree.title == "Older"
    assert [n.code for n in tree.nodes] == ["OLD"]
    assert tree.exam_sections == (("a", "Old section"),)


def test_an_explicit_newest_version_equals_the_default(session: Session) -> None:
    two_versions(session)
    assert get_tree(session, program="demo", subject="sub", version="v2") == get_tree(
        session, program="demo", subject="sub"
    )


def test_trees_of_different_subjects_do_not_mix(session: Session) -> None:
    load_reference(session, reference(subject="one", nodes=[{"code": "ONE", "title": "one"}]))
    load_reference(session, reference(subject="two", nodes=[{"code": "TWO", "title": "two"}]))

    one = get_tree(session, program="demo", subject="one")
    two = get_tree(session, program="demo", subject="two")

    assert one is not None and two is not None
    assert [n.code for n in one.nodes] == ["ONE"]
    assert [n.code for n in two.nodes] == ["TWO"]


def test_get_tree_writes_nothing(session: Session, connection: Connection) -> None:
    load_reference(session, reference())
    session.flush()
    before = table_sizes(connection)

    get_tree(session, program="demo", subject="sub")
    get_tree(session, program="nope", subject="sub")

    assert table_sizes(connection) == before


# =============================================================================================
# GET /v1/programs/{program}/subjects/{subject}/syllabus
# =============================================================================================

URL = "/v1/programs/ib_dp/subjects/physics/syllabus"


@pytest.fixture
def api(connection: Connection, session: Session) -> Iterator[ApiHarness]:
    """The application on this test's transaction (the `api` fixture of tests/api is not
    visible from this directory)."""
    harness = make_harness(connection, session)
    with harness.client:
        yield harness


@pytest.fixture
def loaded(api: ApiHarness) -> SyllabusReference:
    ref = real_reference()
    load_reference(api.session, ref)
    api.session.flush()
    return ref


def test_endpoint_returns_the_tree_in_the_documented_shape(
    api: ApiHarness, loaded: SyllabusReference
) -> None:
    response = api.client.get(URL, headers=api.headers(Role.STUDENT))

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert set(body) == {
        "program",
        "subject",
        "version",
        "title",
        "nodes",
        "exam_sections",
        "command_terms",
    }
    out = SyllabusOut.model_validate(body)
    assert (out.program, out.subject, out.version) == ("ib_dp", "physics", "2025")
    assert out.title == loaded.syllabus_version.title
    assert not hasattr(out, "status")
    assert "status" not in body
    assert [n.code for n in out.nodes] == [n.code for n in loaded.nodes]
    assert {n.code for n in out.nodes if n.is_leaf} == leaf_codes(loaded)
    assert {n.code: n.parent for n in out.nodes} == {n.code: n.parent for n in loaded.nodes}
    assert {n.code: n.attributes for n in out.nodes} == {n.code: n.attributes for n in loaded.nodes}
    assert [(s.code, s.title) for s in out.exam_sections] == [
        (s.code, s.title) for s in loaded.exam_format.sections
    ]
    assert sorted(out.command_terms) == sorted(loaded.exam_format.command_terms)


def test_every_node_object_has_exactly_the_documented_keys(
    api: ApiHarness, loaded: SyllabusReference
) -> None:
    body = api.client.get(URL, headers=api.headers(Role.STUDENT)).json()
    for node in body["nodes"]:
        assert set(node) == {"code", "title", "parent", "is_leaf", "attributes"}
    for section in body["exam_sections"]:
        assert set(section) == {"code", "title"}


def test_endpoint_parents_come_before_children(api: ApiHarness, loaded: SyllabusReference) -> None:
    nodes = api.client.get(URL, headers=api.headers(Role.STUDENT)).json()["nodes"]
    position = {n["code"]: i for i, n in enumerate(nodes)}
    for node in nodes:
        if node["parent"] is not None:
            assert position[node["parent"]] < position[node["code"]]


def test_endpoint_matches_the_service(api: ApiHarness, loaded: SyllabusReference) -> None:
    tree = get_tree(api.session, program="ib_dp", subject="physics")
    assert tree is not None
    body = api.client.get(URL, headers=api.headers(Role.STUDENT)).json()

    assert [n["code"] for n in body["nodes"]] == [n.code for n in tree.nodes]
    assert [n["is_leaf"] for n in body["nodes"]] == [n.is_leaf for n in tree.nodes]
    assert [(s["code"], s["title"]) for s in body["exam_sections"]] == list(tree.exam_sections)
    assert body["command_terms"] == list(tree.command_terms)


@pytest.mark.parametrize("role", ALL_ROLES)
def test_every_role_can_read_the_syllabus(
    api: ApiHarness, loaded: SyllabusReference, role: Role
) -> None:
    assert api.client.get(URL, headers=api.headers(role)).status_code == 200


def test_the_syllabus_needs_a_token(api: ApiHarness, loaded: SyllabusReference) -> None:
    response = api.client.get(URL)
    assert response.status_code == 401
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "unauthenticated"


def test_an_account_without_a_role_gets_404(api: ApiHarness, loaded: SyllabusReference) -> None:
    assert api.client.get(URL, headers=api.headers()).status_code == 404


@pytest.mark.parametrize(
    "path",
    [
        "/v1/programs/nope/subjects/physics/syllabus",
        "/v1/programs/ib_dp/subjects/nope/syllabus",
        "/v1/programs/nope/subjects/nope/syllabus",
        "/v1/programs/IB_DP/subjects/physics/syllabus",
        "/v1/programs/physics/subjects/ib_dp/syllabus",
    ],
)
def test_unknown_codes_are_404_problems(
    api: ApiHarness, loaded: SyllabusReference, path: str
) -> None:
    response = api.client.get(path, headers=api.headers(Role.STUDENT))
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "not_found"


def test_unknown_codes_look_like_a_path_that_does_not_exist(
    api: ApiHarness, loaded: SyllabusReference
) -> None:
    headers = api.headers(Role.STUDENT)
    unknown = api.client.get("/v1/programs/nope/subjects/physics/syllabus", headers=headers)
    nothing = api.client.get("/v1/nothing-here", headers=headers)
    assert unknown.status_code == nothing.status_code == 404
    assert unknown.content == nothing.content


def test_version_query_selects_a_version(api: ApiHarness) -> None:
    older = reference(
        program="ib_dp",
        subject="physics",
        version="2020",
        version_title="Older syllabus",
        nodes=[{"code": "OLD", "title": "Old node"}],
    )
    load_reference(api.session, older)
    time.sleep(0.02)
    load_reference(api.session, real_reference())
    api.session.flush()
    headers = api.headers(Role.STUDENT)

    default = api.client.get(URL, headers=headers).json()
    chosen_old = api.client.get(URL, params={"version": "2020"}, headers=headers)
    chosen_new = api.client.get(URL, params={"version": "2025"}, headers=headers)

    assert default["version"] == "2025"
    assert chosen_old.status_code == 200
    assert chosen_old.json()["version"] == "2020"
    assert chosen_old.json()["title"] == "Older syllabus"
    assert [n["code"] for n in chosen_old.json()["nodes"]] == ["OLD"]
    assert chosen_new.json() == default


def test_unknown_version_is_404(api: ApiHarness, loaded: SyllabusReference) -> None:
    response = api.client.get(URL, params={"version": "1999"}, headers=api.headers(Role.STUDENT))
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_overlong_version_is_rejected_as_invalid(
    api: ApiHarness, loaded: SyllabusReference
) -> None:
    response = api.client.get(URL, params={"version": "9" * 121}, headers=api.headers(Role.STUDENT))
    assert response.status_code == 422
    assert response.json()["code"] == "validation_failed"


def test_endpoint_reads_only(api: ApiHarness, loaded: SyllabusReference) -> None:
    headers = api.headers(Role.STUDENT)
    before = table_sizes(api.session.connection())
    api.client.get(URL, headers=headers)
    api.client.get("/v1/programs/nope/subjects/physics/syllabus", headers=headers)
    assert table_sizes(api.session.connection()) == before


def test_other_methods_are_refused(api: ApiHarness, loaded: SyllabusReference) -> None:
    headers = api.headers(Role.PLATFORM_ADMIN)
    for method in ("post", "put", "delete", "patch"):
        response = getattr(api.client, method)(URL, headers=headers)
        assert response.status_code in (404, 405)


def test_two_programs_do_not_share_trees(api: ApiHarness) -> None:
    load_reference(
        api.session, reference(program="pa", subject="phys", nodes=[{"code": "PA", "title": "t"}])
    )
    load_reference(
        api.session, reference(program="pb", subject="phys", nodes=[{"code": "PB", "title": "t"}])
    )
    api.session.flush()
    headers = api.headers(Role.STUDENT)

    one = api.client.get("/v1/programs/pa/subjects/phys/syllabus", headers=headers).json()
    two = api.client.get("/v1/programs/pb/subjects/phys/syllabus", headers=headers).json()

    assert [n["code"] for n in one["nodes"]] == ["PA"]
    assert [n["code"] for n in two["nodes"]] == ["PB"]
