"""Two first-time redemptions of one invite by the same brand-new person (M1-G slice 9, review
LOW-1): both succeed, the use is counted once. Needs committed connections, so it runs on a
database made for the test."""

from __future__ import annotations

import threading
import uuid
from typing import Any

import pytest
from sqlalchemy import Engine, text
from sqlalchemy.orm import sessionmaker

from qlab.organizations import service as organizations
from qlab.organizations.service import Role

pytestmark = pytest.mark.db

ISSUER = "https://issuer.example.invalid"


@pytest.mark.parametrize("round_", range(6))
def test_the_same_new_person_redeeming_twice_at_once_counts_once(
    throwaway_engine: Engine, round_: int
) -> None:
    factory = sessionmaker(bind=throwaway_engine)
    with factory() as session, session.begin():
        _, code = organizations.create_invite(
            session,
            created_by="cli:owner",
            creator_roles=frozenset({Role.PLATFORM_ADMIN}),
            role=Role.STUDENT,
            expires_in_days=1,
            max_uses=3,
        )
    subject = f"racer-{uuid.uuid4().hex}"
    barrier = threading.Barrier(2)
    results: list[Any] = [None, None]

    def go(index: int) -> None:
        barrier.wait(timeout=30)
        try:
            with factory() as session, session.begin():
                results[index] = organizations.redeem_invite(
                    session, issuer=ISSUER, subject=subject, code=code
                )
        except Exception as error:  # noqa: BLE001 - the test reports what happened
            results[index] = error

    threads = [threading.Thread(target=go, args=(i,)) for i in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert all(isinstance(r, organizations.RedeemResult) for r in results), results
    assert sorted(r.counted for r in results) == [False, True]
    with throwaway_engine.connect() as connection:
        uses = connection.execute(text("SELECT uses FROM invite")).scalar_one()
        redemptions = connection.execute(
            text("SELECT count(*) FROM invite_redemption")
        ).scalar_one()
        accounts = connection.execute(
            text("SELECT count(*) FROM account WHERE subject = :s"), {"s": subject}
        ).scalar_one()
    assert (uses, redemptions, accounts) == (1, 1, 1)
