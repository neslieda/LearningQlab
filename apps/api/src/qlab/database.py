"""Shared persistence plumbing: declarative base, identifiers and engine construction.

Modules own their tables (`<module>/models.py`) and never touch another module's models;
see docs/API_DESIGN.md section 2. This file holds only what every module needs.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Engine, MetaData, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DATABASE_URL_ENV = "QLAB_DATABASE_URL"

# Explicit names keep hand-written migrations and the models comparable.
NAMING_CONVENTION = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map = {datetime: DateTime(timezone=True)}


def new_id() -> uuid.UUID:
    """Time-ordered identifier (UUIDv7). Prefixed forms (`q_...`) exist only at the API edge."""
    return uuid.uuid7()


def created_at_column() -> Mapped[datetime]:
    return mapped_column(server_default=func.now())


def database_url() -> str:
    url = os.environ.get(DATABASE_URL_ENV)
    if not url:
        raise RuntimeError(f"{DATABASE_URL_ENV} is not set")
    return url


def make_engine(url: str | None = None) -> Engine:
    # Statement parameters hold question content; they stay out of error messages and logs.
    return create_engine(url or database_url(), pool_pre_ping=True, hide_parameters=True)
