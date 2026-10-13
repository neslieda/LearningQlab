"""Import of converted pilot files through the content service (docs/pilot/IMPORT_RULES.md §7).

Questions arrive as `authored` drafts under the platform's own rights record (D-52). The import
is idempotent: a question is recognised by its `source_ref`.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from qlab.audit import service as audit
from qlab.content import service as content
from qlab.content.pilot.model import PilotFile
from qlab.rights import service as rights
from qlab.syllabus import service as syllabus

ACTOR = "system:pilot_import"
# The pilot sets were written for this syllabus version (codes of the reference file).
PILOT_SYLLABUS = {"program": "ib_dp", "subject": "physics", "version": "2025"}
# Licence reference of the platform's own-content rights record.
OWN_CONTENT_LICENSE_REF = "platform:own-content"
_EDITABLE = (content.VersionStatus.DRAFT, content.VersionStatus.NEEDS_FIX)


@dataclass
class LoadReport:
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    # Content differs but the latest version is not editable (in review, approved, published…).
    skipped: dict[str, str] = field(default_factory=dict)

    def summary(self) -> str:
        return (
            f"created {len(self.created)}, updated {len(self.updated)}, "
            f"unchanged {len(self.unchanged)}, skipped {len(self.skipped)}"
        )


def read_pilot_files(directory: Path) -> list[PilotFile]:
    """Every converted file in `directory`, by name. An empty directory is an error."""
    paths = sorted(directory.glob("*.json"))
    if not paths:
        raise FileNotFoundError(f"no converted pilot files in {directory}")
    return [PilotFile.model_validate_json(path.read_text(encoding="utf-8")) for path in paths]


def ensure_own_content_rights(session: Session, *, holder: str, actor: str = ACTOR) -> uuid.UUID:
    """The platform's own-content rights record, created (and audited) when none is usable.

    A record is usable when it permits display to everyone now. A revoked or expired one is
    never reused; a new record is opened instead, and the old one stays as history.
    """
    now = datetime.now(UTC)
    for record in rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF):
        if rights.evaluate(record, rights.Purpose.DISPLAY, at=now):
            return record.id
    record = rights.create_record(
        session,
        holder=holder,
        license_ref=OWN_CONTENT_LICENSE_REF,
        valid_from=now,
        display_scope=rights.DisplayScope.ALL,
        allows_ai_processing=True,
        allows_commercial_use=True,
        note="Content written for the platform; the record states the platform's own claim.",
    )
    audit.record(
        session,
        actor=actor,
        action="rights_record.created",
        entity_type="rights_record",
        entity_id=str(record.id),
        data={
            "license_ref": OWN_CONTENT_LICENSE_REF,
            "display_scope": record.display_scope.value,
            "allows_ai_processing": record.allows_ai_processing,
            "allows_commercial_use": record.allows_commercial_use,
        },
    )
    return record.id


def load_pilot(
    session: Session,
    files: Iterable[PilotFile],
    *,
    rights_record_id: uuid.UUID,
    syllabus_version_id: uuid.UUID,
    actor: str = ACTOR,
) -> LoadReport:
    """Create or update one draft question per pilot question, inside the caller's transaction.

    - No question with the `source_ref`: it is created (`authored`, version 1, `draft`).
    - Latest version has the same content hash: nothing happens.
    - Content differs and the latest version is `draft` or `needs_fix`: it is updated.
    - Content differs and the latest version is anything else: nothing happens and the key is
      reported under `skipped` with that status. The import never opens revisions or moves a
      version through the lifecycle.

    Any error from the content service (invalid document, rights, renderer) propagates; the
    caller's transaction decides what survives.
    """
    report = LoadReport()
    for pilot_file in files:
        for question in pilot_file.questions:
            ref = question.source_ref
            existing = content.find_question_by_source_ref(session, ref)
            if existing is None:
                content.create_question(
                    session,
                    actor=actor,
                    document=question.document,
                    rights_record_id=rights_record_id,
                    syllabus_version_id=syllabus_version_id,
                    source_ref=ref,
                )
                report.created.append(ref)
                continue
            latest = content.list_versions(session, existing.id)[-1]
            if latest.content_sha256 == content.content_sha256(question.document):
                report.unchanged.append(ref)
            elif latest.status in _EDITABLE:
                content.update_draft(
                    session, actor=actor, version_id=latest.id, document=question.document
                )
                report.updated.append(ref)
            else:
                report.skipped[ref] = latest.status.value
    return report


def load_pilot_directory(session: Session, directory: Path, *, holder: str) -> LoadReport:
    """`load_pilot` for every converted file in `directory`, resolving rights and syllabus."""
    syllabus_version_id = syllabus.find_syllabus_version(session, **PILOT_SYLLABUS)
    if syllabus_version_id is None:
        raise LookupError("the pilot syllabus version is not loaded (python -m qlab.syllabus …)")
    rights_record_id = ensure_own_content_rights(session, holder=holder)
    return load_pilot(
        session,
        read_pilot_files(directory),
        rights_record_id=rights_record_id,
        syllabus_version_id=syllabus_version_id,
    )
