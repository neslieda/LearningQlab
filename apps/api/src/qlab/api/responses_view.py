"""Stored learner answers at the API edge (M1-G slice 8, D-66; docs/slices/M1G-8-OGRENCI.md).
Implemented in slice 8."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from qlab.api.policy import Principal
from qlab.api.schemas import AnswerRequest, AnswerResult, DeletedOut, ResponsePage


def submit(
    session: Session, *, caller: Principal, question_id: uuid.UUID, answer: AnswerRequest
) -> AnswerResult:
    raise NotImplementedError


def list_page(
    session: Session,
    *,
    caller: Principal,
    question_id: uuid.UUID | None,
    cursor: str | None,
    limit: int,
) -> ResponsePage:
    raise NotImplementedError


def delete_all(session: Session, *, caller: Principal) -> DeletedOut:
    raise NotImplementedError
