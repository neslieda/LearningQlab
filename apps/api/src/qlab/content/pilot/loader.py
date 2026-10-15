"""Import of converted pilot files through the content service (docs/pilot/IMPORT_RULES.md §7).

Questions arrive as `authored` drafts under the platform's own rights record (D-52, D-58). The
import is idempotent (a question is recognised by its `source_ref`) and conservative: it never
opens a rights record on its own, never works around a revoked one, never overwrites a draft
somebody edited, and never moves a version through the lifecycle.
"""

from __future__ import annotations

import hashlib
import uuid
from collections.abc import Sequence
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
# Licence reference of the platform's own-content rights record, and what that record permits
# (owner decision D-58).
OWN_CONTENT_LICENSE_REF = "platform:own-content"
_IMPORT_ACTIONS = ("question_version.created", "question_version.updated")


class OwnContentRightsError(Exception):
    """The platform's own-content rights record is missing, ambiguous, revoked, expired or not
    what the import expects. A human has to decide; the import does not."""


class SourceMismatch(Exception):
    """A converted file is not the conversion of the Markdown file it names."""


@dataclass
class LoadReport:
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    # Content differs but the version was left alone: the value is "edited" when somebody
    # changed the draft after the last import, else the version's status.
    skipped: dict[str, str] = field(default_factory=dict)
    # A question with the key exists but its rights record does not permit display.
    blocked: list[str] = field(default_factory=list)

    def counts(self) -> dict[str, int]:
        return {
            "created": len(self.created),
            "updated": len(self.updated),
            "unchanged": len(self.unchanged),
            "skipped": len(self.skipped),
            "blocked": len(self.blocked),
        }

    def summary(self) -> str:
        return ", ".join(f"{name} {count}" for name, count in self.counts().items())


def read_pilot_files(directory: Path) -> list[PilotFile]:
    """Every converted file in `directory`, by name. An empty directory is an error."""
    paths = sorted(directory.glob("*.json"))
    if not paths:
        raise FileNotFoundError(f"no converted pilot files in {directory}")
    return [PilotFile.model_validate_json(path.read_text(encoding="utf-8")) for path in paths]


def verify_sources(root: Path, files: Sequence[PilotFile]) -> None:
    """Raise SourceMismatch unless every file's `source_sha256` is the SHA-256 of the Markdown
    file it names under `root` (a missing Markdown file is a mismatch too).

    What is imported under the platform's own-content claim must be the conversion of the
    project's own pilot files, not a stale or hand-made JSON.
    """
    for pilot_file in files:
        source = root / pilot_file.source_file
        if not source.is_file():
            raise SourceMismatch(f"{pilot_file.source_file} does not exist under {root}")
        if hashlib.sha256(source.read_bytes()).hexdigest() != pilot_file.source_sha256:
            raise SourceMismatch(
                f"{pilot_file.source_file} has changed since it was converted; run convert again"
            )


def find_own_content_rights(session: Session, *, holder: str) -> uuid.UUID | None:
    """Id of the platform's own-content rights record, or None when no record with the licence
    reference `OWN_CONTENT_LICENSE_REF` exists at all.

    Raises OwnContentRightsError when records with that reference exist but the import must
    not go on: any of them is revoked, expired or not yet valid (a revocation is a takedown
    decision and is not worked around with a new record); there is more than one; or the one
    record is not exactly what is expected — the given `holder`, display to everyone, AI
    processing and commercial use permitted, no end of validity.
    """
    records = rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)
    if not records:
        return None
    now = datetime.now(UTC)
    if any(r.revoked_at is not None or not (r.valid_from <= now) for r in records) or any(
        r.valid_until is not None for r in records
    ):
        raise OwnContentRightsError(
            f"a {OWN_CONTENT_LICENSE_REF} rights record is revoked, expired or limited in time; "
            "the import does not replace it"
        )
    if len(records) > 1:
        raise OwnContentRightsError(f"more than one {OWN_CONTENT_LICENSE_REF} rights record")
    record = records[0]
    expected = (
        record.holder == holder
        and record.display_scope is rights.DisplayScope.ALL
        and record.allows_ai_processing is True
        and record.allows_commercial_use is True
    )
    if not expected:
        raise OwnContentRightsError(
            f"the {OWN_CONTENT_LICENSE_REF} rights record does not have the expected holder "
            "and permissions"
        )
    return record.id


def create_own_content_rights(
    session: Session, *, holder: str, operator: str, actor: str = ACTOR
) -> uuid.UUID:
    """Open the platform's own-content rights record and audit it. An explicit step.

    Permissions per D-58: display to everyone, AI processing and commercial use, valid from now
    with no end. Raises OwnContentRightsError when any record with the licence reference already
    exists (usable or not). The audit entry `rights_record.created` carries the holder, the
    permissions, the start of validity and `operator`, the opaque account id of the person who
    ran the import (ValueError if it is not a valid audit actor).
    """
    if rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF):
        raise OwnContentRightsError(f"a {OWN_CONTENT_LICENSE_REF} rights record already exists")
    _require_operator(operator)
    record = rights.create_record(
        session,
        holder=holder,
        license_ref=OWN_CONTENT_LICENSE_REF,
        valid_from=datetime.now(UTC),
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
            "operator": operator,
            "holder": record.holder,
            "license_ref": OWN_CONTENT_LICENSE_REF,
            "display_scope": record.display_scope.value,
            "allows_ai_processing": record.allows_ai_processing,
            "allows_commercial_use": record.allows_commercial_use,
            "valid_from": record.valid_from.isoformat(),
        },
    )
    return record.id


def _require_operator(operator: str) -> None:
    if not audit.is_valid_actor(operator) or operator.startswith("system:"):
        raise ValueError("operator must be the opaque account id of a person")


def _last_imported_hash(session: Session, version_id: uuid.UUID, actor: str) -> str | None:
    """The content hash the importer last wrote to this version, from the audit log."""
    written = [
        entry.data.get("content_sha256")
        for entry in audit.entries_for(session, "question_version", str(version_id))
        if entry.actor == actor and entry.action in _IMPORT_ACTIONS
    ]
    return written[-1] if written else None


def load_pilot(
    session: Session,
    files: Sequence[PilotFile],
    *,
    rights_record_id: uuid.UUID,
    syllabus_version_id: uuid.UUID,
    operator: str,
    actor: str = ACTOR,
) -> LoadReport:
    """Create or update one draft question per pilot question, inside the caller's transaction.

    For each question, by its `source_ref`:

    - no such question: it is created (`authored`, version 1, `draft`) → `created`;
    - the latest version has the same content hash → `unchanged`;
    - content differs, the latest version is `draft` and still holds exactly what the importer
      last wrote to it (its hash equals the hash in the importer's last audit entry for that
      version) → it is updated → `updated`;
    - content differs and the draft was changed by anyone else since → `skipped` with the
      value "edited"; a human edit is never overwritten;
    - content differs and the latest version is in any other status (including `needs_fix`)
      → `skipped` with that status;
    - a question with the key exists but its rights record does not permit display →
      `blocked`; nothing is created.

    The import never opens revisions and never changes a version's status. It ends by writing
    one audit entry `pilot_import.completed` (entity type `pilot_import`, entity id the
    operator) with the operator, the counts and each file's `source_file` and `source_sha256`.
    `operator` is the opaque account id of the person running the import (ValueError otherwise,
    before anything is written). The same key twice in one call is a ValueError.

    Any error from the content service (invalid document, rights, renderer) propagates; the
    caller's transaction decides what survives.
    """
    _require_operator(operator)
    refs = [q.source_ref for f in files for q in f.questions]
    if len(refs) != len(set(refs)):
        raise ValueError("the same source_ref occurs more than once in the files")
    report = LoadReport()
    for pilot_file in files:
        for question in pilot_file.questions:
            ref = question.source_ref
            existing = content.find_question_by_source_ref(session, ref)
            if existing is None:
                try:
                    content.create_question(
                        session,
                        actor=actor,
                        document=question.document,
                        rights_record_id=rights_record_id,
                        syllabus_version_id=syllabus_version_id,
                        source_ref=ref,
                    )
                except content.DuplicateSourceRef:
                    report.blocked.append(ref)
                else:
                    report.created.append(ref)
                continue
            latest = content.list_versions(session, existing.id)[-1]
            if latest.content_sha256 == content.content_sha256(question.document):
                report.unchanged.append(ref)
            elif latest.status is not content.VersionStatus.DRAFT:
                report.skipped[ref] = latest.status.value
            elif _last_imported_hash(session, latest.id, actor) != latest.content_sha256:
                report.skipped[ref] = "edited"
            else:
                content.update_draft(
                    session,
                    actor=actor,
                    version_id=latest.id,
                    document=question.document,
                    expected_content_sha256=latest.content_sha256,
                )
                report.updated.append(ref)
    audit.record(
        session,
        actor=actor,
        action="pilot_import.completed",
        entity_type="pilot_import",
        entity_id=operator,
        data={
            "operator": operator,
            "counts": report.counts(),
            "files": {f.source_file: f.source_sha256 for f in files},
        },
    )
    return report


def load_pilot_directory(
    session: Session,
    root: Path,
    *,
    holder: str,
    operator: str,
    create_rights: bool = False,
) -> LoadReport:
    """`load_pilot` for every converted file under `<root>/content/pilot`.

    In order, and before anything is written: the files are read; `verify_sources(root, …)`;
    the pilot syllabus version must be loaded (LookupError); the own-content rights record is
    looked up with `find_own_content_rights`. If there is none it is opened with
    `create_own_content_rights` when `create_rights` is true, else OwnContentRightsError.
    """
    files = read_pilot_files(root / "content" / "pilot")
    verify_sources(root, files)
    syllabus_version_id = syllabus.find_syllabus_version(session, **PILOT_SYLLABUS)
    if syllabus_version_id is None:
        raise LookupError("the pilot syllabus version is not loaded (python -m qlab.syllabus …)")
    _require_operator(operator)
    rights_record_id = find_own_content_rights(session, holder=holder)
    if rights_record_id is None:
        if not create_rights:
            raise OwnContentRightsError(
                f"no {OWN_CONTENT_LICENSE_REF} rights record exists; "
                "open it explicitly with --create-rights"
            )
        rights_record_id = create_own_content_rights(session, holder=holder, operator=operator)
    return load_pilot(
        session,
        files,
        rights_record_id=rights_record_id,
        syllabus_version_id=syllabus_version_id,
        operator=operator,
    )
