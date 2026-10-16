"""Editor manifest: committed file matches generation and agrees with the Pydantic node models."""

import json
import re
from pathlib import Path
from typing import Any

import pytest

from qlab.content.schema import blocks
from qlab.content.schema.manifest import MANIFEST_PATH, build_manifest, render

PILOT_DIR = Path(__file__).resolve().parents[4] / "content" / "pilot"
MANIFEST = build_manifest()


def _members(union: Any) -> list[Any]:
    from qlab.content.schema.manifest import union_members

    return union_members(union)


def _name(model: Any) -> str:
    return str(model.model_fields["type"].annotation.__args__[0])


def test_committed_manifest_equals_fresh_generation() -> None:
    assert MANIFEST_PATH.read_text(encoding="utf-8") == render()


def test_node_names_equal_models_accepted() -> None:
    expected = {"doc", "list_item", "table_row", "text"}
    for union in (blocks.Block, blocks.Inline, blocks.Cell):
        expected |= {_name(m) for m in _members(union)}
    assert set(MANIFEST["nodes"]) == expected


def test_mark_names_equal_enum_in_order() -> None:
    assert [m["name"] for m in MANIFEST["marks"]] == [m.value for m in blocks.MarkType]
    for pair in MANIFEST["mark_exclusions"]:
        assert all(n in {m.value for m in blocks.MarkType} for n in pair)


def test_attrs_match_model_fields() -> None:
    models = {_name(m): m for u in (blocks.Block, blocks.Inline, blocks.Cell) for m in _members(u)}
    models.update({"doc": blocks.Doc, "list_item": blocks.ListItem, "table_row": blocks.TableRow})
    for name, node in MANIFEST["nodes"].items():
        attrs_field = models[name].model_fields.get("attrs")
        model_attrs = set(attrs_field.annotation.model_fields) if attrs_field else set()
        assert set(node["attrs"]) == model_attrs, name
        assert node["marks"] == ("marks" in models[name].model_fields), name


def _walk(node: Any, seen: list[tuple[str, list[str]]]) -> None:
    if isinstance(node, dict):
        if isinstance(node.get("type"), str) and node["type"] in MANIFEST["nodes"]:
            kids = node.get("content", [])
            if isinstance(kids, list):
                seen.append((node["type"], [k["type"] for k in kids]))
        for v in node.values():
            _walk(v, seen)
    elif isinstance(node, list):
        for v in node:
            _walk(v, seen)


def _allowed(expr: str) -> set[str]:
    groups = {
        g: {n for n, d in MANIFEST["nodes"].items() if d["group"] == g} for g in ("block", "inline")
    }
    return {t for token in re.findall(r"[a-z_]+", expr) for t in (groups.get(token) or {token})}


@pytest.mark.parametrize("path", sorted(PILOT_DIR.glob("*.json")), ids=lambda p: p.stem)
def test_pilot_documents_fit_content_expressions(path: Path) -> None:
    seen: list[tuple[str, list[str]]] = []
    _walk(json.loads(path.read_text(encoding="utf-8")), seen)
    for parent, kids in seen:
        expr = MANIFEST["nodes"][parent]["content"]
        if kids:
            assert expr is not None, parent
            assert set(kids) <= _allowed(expr), (parent, kids)
            continue
        assert expr is None or not expr.endswith("+"), parent
