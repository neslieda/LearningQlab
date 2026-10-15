from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import Connection
from sqlalchemy.orm import Session

from tests.api.support import ApiHarness, make_harness


@pytest.fixture
def api(connection: Connection, session: Session) -> Iterator[ApiHarness]:
    """The application on this test's transaction (separation of duties off)."""
    harness = make_harness(connection, session)
    with harness.client:
        yield harness
