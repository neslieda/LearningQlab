"""The committed OpenAPI document (docs/API_DESIGN.md section 6, SOZLESME sections 2 and 4).

No database is needed: the document is built from the application without connecting.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from qlab.api import openapi
from qlab.api.policy import ENDPOINT_POLICY

HTTP_METHODS = {"get", "put", "post", "delete", "patch", "head", "options", "trace"}
ANSWER_FIELDS = {
    "correct_key",
    "rationale",
    "explanation",
    "outcome",
    "description",
    "mark_points",
    "notes",
    "solution_model",
}


@pytest.fixture(scope="module")
def committed() -> dict[str, Any]:
    document: dict[str, Any] = json.loads(openapi.OPENAPI_FILE.read_text(encoding="utf-8"))
    return document


def operations(document: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    return [
        (method.upper(), path, operation)
        for path, item in document["paths"].items()
        for method, operation in item.items()
        if method in HTTP_METHODS
    ]


def test_the_committed_file_is_what_the_application_generates() -> None:
    assert openapi.OPENAPI_FILE.is_file()
    assert openapi.OPENAPI_FILE.read_text(encoding="utf-8") == openapi.render()


def test_the_check_command_passes_on_the_committed_file(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert openapi.main(["--check"]) == 0
    assert "current" in capsys.readouterr().out


def test_the_check_command_fails_on_a_stale_file(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    stale = tmp_path / "openapi.json"
    stale.write_text(openapi.render().replace('"title"', '"titel"', 1), encoding="utf-8")
    monkeypatch.setattr(openapi, "OPENAPI_FILE", stale)
    assert openapi.main(["--check"]) == 1
    assert "out of date" in capsys.readouterr().err
    missing = tmp_path / "missing.json"
    monkeypatch.setattr(openapi, "OPENAPI_FILE", missing)
    assert openapi.main(["--check"]) == 1
    assert not missing.exists()  # --check never writes


def test_rendering_is_deterministic() -> None:
    assert openapi.render() == openapi.render()
    assert openapi.render().endswith("\n")


def test_every_operation_except_healthz_requires_a_bearer_token(committed: dict[str, Any]) -> None:
    assert committed["components"]["securitySchemes"]["bearer"]["scheme"] == "bearer"
    for method, path, operation in operations(committed):
        if path == "/healthz":
            assert operation["security"] == [], (method, path)
        else:
            assert operation["security"] == [{"bearer": []}], (method, path)


def test_the_paths_and_methods_are_exactly_the_policy_table(committed: dict[str, Any]) -> None:
    documented = {(method, path) for method, path, _ in operations(committed)}
    assert documented == set(ENDPOINT_POLICY)
    assert len(documented) == 25


def test_operation_ids_are_present_and_unique(committed: dict[str, Any]) -> None:
    found = [operation.get("operationId") for _, _, operation in operations(committed)]
    assert all(isinstance(i, str) and i for i in found)
    assert len(found) == len(set(found))


def test_every_operation_declares_the_stable_error_shape(committed: dict[str, Any]) -> None:
    for method, path, operation in operations(committed):
        if path == "/healthz":
            continue
        assert "401" in operation["responses"], (method, path)
        assert "404" in operation["responses"], (method, path)


def test_state_changing_endpoints_document_their_conflicts(committed: dict[str, Any]) -> None:
    paths = committed["paths"]
    for suffix in (
        "submit",
        "approve",
        "request-changes",
        "reject",
        "publish",
        "withdraw",
        "republish",
    ):
        operation = paths[f"/v1/admin/question-versions/{{version_id}}/{suffix}"]["post"]
        assert "409" in operation["responses"], suffix
    assert "403" in paths["/v1/admin/question-versions/{version_id}/approve"]["post"]["responses"]
    assert "409" in paths["/v1/admin/question-versions/{version_id}"]["put"]["responses"]
    revisions = paths["/v1/admin/questions/{question_id}/revisions"]["post"]
    assert "201" in revisions["responses"]


def test_no_learner_schema_has_a_property_named_like_an_answer(committed: dict[str, Any]) -> None:
    schemas = committed["components"]["schemas"]
    learner = {name: schema for name, schema in schemas.items() if name.startswith("Learner")}
    assert learner  # the family exists
    for name, schema in learner.items():
        leaked = ANSWER_FIELDS & set(schema.get("properties", {}))
        assert not leaked, (name, leaked)
        assert schema.get("additionalProperties") is False, name


def reachable(document: dict[str, Any], start: Any) -> set[str]:
    """Names of the component schemas reachable from a JSON fragment through `$ref`."""
    found: set[str] = set()
    pending = [start]
    while pending:
        node = pending.pop()
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str):
                name = ref.rsplit("/", 1)[-1]
                if name not in found:
                    found.add(name)
                    pending.append(document["components"]["schemas"][name])
            pending.extend(node.values())
        elif isinstance(node, list):
            pending.extend(node)
    return found


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/v1/questions"),
        ("get", "/v1/questions/{question_id}"),
    ],
)
def test_the_learner_read_endpoints_return_only_learner_types(
    committed: dict[str, Any], method: str, path: str
) -> None:
    operation = committed["paths"][path][method]
    names = reachable(committed, operation["responses"]["200"])
    assert names
    assert not {n for n in names if n.startswith("Admin")}
    assert "QuestionDocument" not in names
    assert "AdminVersion" not in names


def test_admin_schemas_are_not_reachable_from_the_check_endpoint_request_or_response(
    committed: dict[str, Any],
) -> None:
    operation = committed["paths"]["/v1/questions/{question_id}/check"]["post"]
    names = reachable(committed, operation["requestBody"]) | reachable(
        committed, operation["responses"]["200"]
    )
    assert not {n for n in names if n.startswith("Admin")}
    assert "QuestionDocument" not in names


def test_staff_list_and_decision_schemas_carry_no_document(committed: dict[str, Any]) -> None:
    schemas = committed["components"]["schemas"]
    for name in ("AdminQuestionSummary", "AdminQuestion", "AdminVersionSummary", "VersionStateOut"):
        assert "document" not in schemas[name]["properties"], name
    assert "document" in schemas["AdminVersion"]["properties"]


def test_the_staff_decisions_return_the_version_state_type(committed: dict[str, Any]) -> None:
    for suffix in (
        "submit",
        "approve",
        "request-changes",
        "reject",
        "publish",
        "withdraw",
        "republish",
    ):
        operation = committed["paths"][f"/v1/admin/question-versions/{{version_id}}/{suffix}"][
            "post"
        ]
        body = json.dumps(operation["responses"]["200"])
        assert "VersionStateOut" in body, suffix
