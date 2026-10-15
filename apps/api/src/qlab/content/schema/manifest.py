"""Editor manifest derived from the Pydantic node models (docs/slices/M1G-7B-EDITOR.md section 3).

`python -m qlab.content.schema.manifest` writes packages/question-editor/src/manifest.json;
`--check` exits 1 when the committed file differs from a fresh generation.
Nothing here lists node names by hand: nodes come from the Doc/Block/Inline/Cell unions and
their field annotations.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from typing import Annotated, Any, Union, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from qlab.content.schema import blocks
from qlab.content.schema.blocks import EXCLUSIVE_MARKS, Doc, MarkType

SCHEMA_VERSION = "1.0"
MANIFEST_PATH = Path(__file__).resolve().parents[6] / "packages/question-editor/src/manifest.json"

# Named unions of blocks.py that become ProseMirror groups.
_GROUPS: dict[str, Any] = {"block": blocks.Block, "inline": blocks.Inline}


def union_members(annotation: Any) -> list[type[BaseModel]]:
    origin = get_origin(annotation)
    if origin is Annotated:
        return union_members(get_args(annotation)[0])
    if origin in (Union, types.UnionType):
        out: list[type[BaseModel]] = []
        for arg in get_args(annotation):
            out.extend(union_members(arg))
        return out
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return [annotation]
    raise TypeError(f"unsupported annotation {annotation!r}")


def _type_name(model: type[BaseModel]) -> str:
    (name,) = get_args(model.model_fields["type"].annotation)
    return str(name)


def _names(models: list[type[BaseModel]]) -> set[str]:
    return {_type_name(m) for m in models}


def _element_annotation(field: FieldInfo) -> Any:
    args = get_args(field.annotation)  # tuple[X, ...]
    return args[0]


def _min_length(field: FieldInfo) -> int:
    return max((getattr(m, "min_length", 0) or 0 for m in field.metadata), default=0)


def _content_expr(field: FieldInfo) -> str:
    members = union_members(_element_annotation(field))
    names = sorted(_names(members))
    for group, union in _GROUPS.items():
        if _names(union_members(union)) == set(names):
            atom = group
            break
    else:
        atom = names[0] if len(names) == 1 else "(" + "|".join(names) + ")"
    return atom + ("+" if _min_length(field) >= 1 else "*")


def _attrs(model: type[BaseModel]) -> dict[str, Any]:
    schema = model.model_json_schema()
    out: dict[str, Any] = {}
    for name, prop in schema["properties"].items():
        field = model.model_fields[name]
        kinds = [p["type"] for p in prop.get("anyOf", [prop]) if p.get("type") != "null"]
        entry: dict[str, Any] = {
            "type": kinds[0],
            "required": field.is_required(),
            "default": None
            if field.is_required()
            else field.get_default(call_default_factory=True),
            "pattern": None,
        }
        for src in [prop, *prop.get("anyOf", [])]:
            for key, dest in (
                ("pattern", "pattern"),
                ("minimum", "minimum"),
                ("maximum", "maximum"),
                ("minLength", "minLength"),
            ):
                if key in src:
                    entry[dest] = src[key]
        out[name] = entry
    return out


def _node(model: type[BaseModel], node_group: str | None) -> dict[str, Any]:
    fields = model.model_fields
    content = _content_expr(fields["content"]) if "content" in fields else None
    attrs_model: Any = fields["attrs"].annotation if "attrs" in fields else None
    return {
        "group": node_group,
        "content": content,
        "atom": content is None and "text" not in fields,
        "marks": "marks" in fields,
        "attrs": _attrs(attrs_model) if attrs_model is not None else {},
    }


def _reachable(model: type[BaseModel], seen: dict[str, type[BaseModel]]) -> None:
    name = _type_name(model)
    if name in seen:
        return
    seen[name] = model
    if "content" in model.model_fields:
        for child in union_members(_element_annotation(model.model_fields["content"])):
            _reachable(child, seen)


def build_manifest() -> dict[str, Any]:
    models: dict[str, type[BaseModel]] = {}
    _reachable(Doc, models)
    group_of: dict[str, str] = {}
    for group, union in _GROUPS.items():
        for member in union_members(union):
            group_of[_type_name(member)] = group
    nodes = {name: _node(model, group_of.get(name)) for name, model in sorted(models.items())}
    return {
        "schema_version": SCHEMA_VERSION,
        "top": _type_name(Doc),
        "marks": [{"name": m.value} for m in MarkType],
        "mark_exclusions": [[a.value, b.value] for a, b in EXCLUSIVE_MARKS],
        "nodes": nodes,
    }


def render() -> str:
    return json.dumps(build_manifest(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    fresh = render()
    if "--check" in argv:
        current = MANIFEST_PATH.read_text(encoding="utf-8") if MANIFEST_PATH.exists() else ""
        if current != fresh:
            print(f"{MANIFEST_PATH} is out of date; run python -m qlab.content.schema.manifest")
            return 1
        return 0
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(fresh, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
