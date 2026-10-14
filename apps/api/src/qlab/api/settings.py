"""Runtime settings, read once at start-up. A setting that is missing or unsafe stops the
application from starting; nothing falls back to a permissive default.

| Variable | Meaning |
|---|---|
| `QLAB_ENV` | `local`, `staging` or `production`. Required. |
| `QLAB_FORBID_SELF_APPROVAL` | `true` / `false`: the last editor of a version cannot approve it (D-59). Defaults to `false` locally; must be `true` anywhere else. |
| `QLAB_DEV_KEY_FILE` | Local only: the development signing key (default `~/.qlab/dev-signing-key.pem`). Refused outside `local`. |
| `QLAB_DATABASE_URL` | See `qlab.database`. |
"""  # noqa: E501

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from qlab.identity import devkey
from qlab.identity.tokens import DEV_AUDIENCE, DEV_ISSUER, TokenVerifier

ENVIRONMENT_ENV = "QLAB_ENV"
FORBID_SELF_APPROVAL_ENV = "QLAB_FORBID_SELF_APPROVAL"


class StartupError(RuntimeError):
    """The application refuses to start with this configuration."""


class Environment(StrEnum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass(frozen=True)
class Settings:
    environment: Environment
    forbid_self_approval: bool
    # Where the development signing key is. None outside the local environment.
    dev_key_file: Path | None = None

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        environ = os.environ if environ is None else environ
        raw = environ.get(ENVIRONMENT_ENV, "")
        try:
            environment = Environment(raw)
        except ValueError:
            names = ", ".join(e.value for e in Environment)
            raise StartupError(f"{ENVIRONMENT_ENV} must be one of: {names}") from None
        local = environment is Environment.LOCAL

        flag = environ.get(FORBID_SELF_APPROVAL_ENV)
        if flag is None:
            forbid = not local
        elif flag in ("true", "false"):
            forbid = flag == "true"
        else:
            raise StartupError(f"{FORBID_SELF_APPROVAL_ENV} must be true or false")

        key_file = environ.get(devkey.DEV_KEY_FILE_ENV)
        if not local and key_file:
            raise StartupError(
                f"{devkey.DEV_KEY_FILE_ENV} is set: the development signing key is refused "
                f"outside the local environment"
            )
        settings = cls(
            environment=environment,
            forbid_self_approval=forbid,
            dev_key_file=(Path(key_file) if key_file else devkey.default_path()) if local else None,
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        """StartupError when the combination is not allowed."""
        if self.environment is Environment.LOCAL:
            return
        if self.dev_key_file is not None:
            raise StartupError(
                "the development signing key is refused outside the local environment"
            )
        if not self.forbid_self_approval:
            # Opening the rule is a condition of going on the web (D-59, M1-G slice 9).
            raise StartupError(
                "separation of duties must be on outside the local environment: "
                f"{FORBID_SELF_APPROVAL_ENV}=true"
            )


def check_verifier(settings: Settings, verifier: TokenVerifier) -> None:
    """StartupError when this verifier may not be used in this environment: tokens of the
    local development issuer are accepted in the local environment only."""
    if settings.environment is not Environment.LOCAL and verifier.issuer == DEV_ISSUER:
        raise StartupError(
            "tokens of the local development issuer are refused outside the local environment"
        )


def build_verifier(settings: Settings) -> TokenVerifier:
    """The token verifier for this environment.

    Locally: the public half of the development key, for `DEV_ISSUER` / `DEV_AUDIENCE`; a
    missing or unsafe key file is a StartupError that says how to create one. Elsewhere there
    is no identity provider yet (M1-G slice 9): StartupError.
    """
    settings.validate()
    if settings.environment is not Environment.LOCAL or settings.dev_key_file is None:
        raise StartupError(
            f"no identity provider is configured for the {settings.environment.value} "
            f"environment (M1-G slice 9)"
        )
    try:
        key = devkey.load(settings.dev_key_file)
    except devkey.DevKeyError as error:
        raise StartupError(
            f"{error}. Create the local accounts and key with `python -m qlab.api.dev init`."
        ) from None
    return TokenVerifier(public_keys=[key.public_key()], issuer=DEV_ISSUER, audience=DEV_AUDIENCE)
