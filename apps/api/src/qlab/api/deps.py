"""What handlers share: the caller and the unit of work.

Handlers are plain functions (FastAPI runs them in a worker thread) and open their transaction
explicitly, so that the commit has happened before the response is built.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from qlab.api.policy import Principal, principal
from qlab.api.settings import Settings

Caller = Annotated[Principal, Depends(principal)]


def settings(request: Request) -> Settings:
    current: Settings = request.app.state.settings
    return current


CurrentSettings = Annotated[Settings, Depends(settings)]


def _factory(request: Request) -> sessionmaker[Session]:
    factory: sessionmaker[Session] = request.app.state.session_factory
    return factory


@contextmanager
def writing(request: Request) -> Iterator[Session]:
    """A transaction that commits when the block ends and rolls back when it raises."""
    with _factory(request)() as session, session.begin():
        yield session


@contextmanager
def reading(request: Request) -> Iterator[Session]:
    """A read-only transaction, enforced by the database and always rolled back. Every learner
    endpoint uses it: a learner request cannot write anything, whatever the handler does."""
    with _factory(request)() as session:
        session.begin()
        try:
            session.execute(text("SET TRANSACTION READ ONLY"))
            yield session
        finally:
            session.rollback()
