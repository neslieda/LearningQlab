import importlib
import pkgutil

import qlab

# Module list from docs/API_DESIGN.md section 2, plus the pipeline orchestration layer.
EXPECTED_MODULES = {
    "analytics",
    "attempts",
    "audit",
    "content",
    "entitlements",
    "exams",
    "generation",
    "identity",
    "ingestion",
    "llm",
    "marking",
    "organizations",
    "pipeline",
    "review",
    "rights",
    "syllabus",
    "verification",
}


def test_modules_match_documented_list() -> None:
    found = {m.name for m in pkgutil.iter_modules(qlab.__path__) if m.ispkg}
    assert found == EXPECTED_MODULES


def test_every_module_imports() -> None:
    for name in EXPECTED_MODULES:
        importlib.import_module(f"qlab.{name}")
