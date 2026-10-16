"""Runtime settings, read once at start-up. A setting that is missing or unsafe stops the
application from starting; nothing falls back to a permissive default.

| Variable | Meaning |
|---|---|
| `QLAB_ENV` | `local`, `staging` or `production`. Required. |
| `QLAB_FORBID_SELF_APPROVAL` | `true` / `false`: the last editor of a version cannot approve it (D-59). Defaults to `false` locally; must be `true` anywhere else. |
| `QLAB_DEV_KEY_FILE` | Local only: the development signing key (default `~/.qlab/dev-signing-key.pem`). Refused outside `local`. |
| `QLAB_OIDC_ISSUER` | Outside `local`: the identity provider's issuer, exactly as in its discovery document. |
| `QLAB_OIDC_AUDIENCE` | Outside `local`: the audience tokens must contain (Zitadel: the project id). |
| `QLAB_OIDC_CLIENT_ID` | Outside `local`: the client id tokens must name in `azp`. |
| `QLAB_OIDC_STAFF_ORG_ID` | Outside `local`: the identity provider organisation of staff sign-ins (two-step verification); staff roles count only for it. |
| `QLAB_DATABASE_URL` | See `qlab.database`. |
"""  # noqa: E501

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from qlab.identity import devkey
from qlab.identity.oidc import OidcTokenVerifier, OidcUnavailable
from qlab.identity.tokens import DEV_AUDIENCE, DEV_ISSUER, TokenVerifier

ENVIRONMENT_ENV = "QLAB_ENV"
FORBID_SELF_APPROVAL_ENV = "QLAB_FORBID_SELF_APPROVAL"
OIDC_ISSUER_ENV = "QLAB_OIDC_ISSUER"
OIDC_AUDIENCE_ENV = "QLAB_OIDC_AUDIENCE"
OIDC_CLIENT_ID_ENV = "QLAB_OIDC_CLIENT_ID"
OIDC_STAFF_ORG_ENV = "QLAB_OIDC_STAFF_ORG_ID"


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
    # Identity provider organisation of staff sign-ins (two-step verification enforced there).
    # Required outside the local environment; None locally.
    staff_organization: str | None = None
    # The identity provider (outside the local environment).
    oidc_issuer: str | None = None
    oidc_audience: str | None = None
    oidc_client_id: str | None = None

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
        oidc: dict[str, str | None] = {}
        if not local:
            missing = [
                name
                for name in (
                    OIDC_ISSUER_ENV,
                    OIDC_AUDIENCE_ENV,
                    OIDC_CLIENT_ID_ENV,
                    OIDC_STAFF_ORG_ENV,
                )
                if not environ.get(name, "").strip()
            ]
            if missing:
                raise StartupError(f"missing settings: {', '.join(missing)}")
            oidc = {
                "oidc_issuer": environ[OIDC_ISSUER_ENV].strip(),
                "oidc_audience": environ[OIDC_AUDIENCE_ENV].strip(),
                "oidc_client_id": environ[OIDC_CLIENT_ID_ENV].strip(),
                "staff_organization": environ[OIDC_STAFF_ORG_ENV].strip(),
            }
        settings = cls(
            environment=environment,
            forbid_self_approval=forbid,
            dev_key_file=(Path(key_file) if key_file else devkey.default_path()) if local else None,
            **oidc,
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
    missing or unsafe key file is a StartupError that says how to create one. Elsewhere: the
    identity provider's keys, found through its discovery document, which is fetched now; an
    unreachable or unusable provider is a StartupError (M1-G slice 9).
    """
    settings.validate()
    if settings.environment is not Environment.LOCAL:
        if not (settings.oidc_issuer and settings.oidc_audience and settings.oidc_client_id):
            raise StartupError("the identity provider is not configured")
        try:
            return OidcTokenVerifier(
                issuer=settings.oidc_issuer,
                audience=settings.oidc_audience,
                client_id=settings.oidc_client_id,
            )
        except OidcUnavailable as error:
            raise StartupError(f"the identity provider cannot be used: {error}") from None
    if settings.dev_key_file is None:
        raise StartupError("no development key file is configured")
    try:
        key = devkey.load(settings.dev_key_file)
    except devkey.DevKeyError as error:
        raise StartupError(
            f"{error}. Create the local accounts and key with `python -m qlab.api.dev init`."
        ) from None
    return TokenVerifier(public_keys=[key.public_key()], issuer=DEV_ISSUER, audience=DEV_AUDIENCE)
