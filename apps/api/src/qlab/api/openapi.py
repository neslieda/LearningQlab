"""Writes or checks the committed OpenAPI document (docs/API_DESIGN.md section 6).

python -m qlab.api.openapi            # write apps/api/openapi.json
python -m qlab.api.openapi --check    # exit 1 when the file is out of date
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from qlab.api.app import create_app
from qlab.api.errors import PROBLEM_MEDIA_TYPE
from qlab.api.settings import Environment, Settings
from qlab.identity.tokens import DEV_AUDIENCE, DEV_ISSUER, TokenVerifier

OPENAPI_FILE = Path(__file__).resolve().parents[3] / "openapi.json"


def document() -> dict[str, Any]:
    """The OpenAPI document of the application. Needs no database, key or renderer."""
    app = create_app(
        Settings(environment=Environment.LOCAL, forbid_self_approval=False),
        verifier=TokenVerifier(
            public_keys=[Ed25519PrivateKey.generate().public_key()],
            issuer=DEV_ISSUER,
            audience=DEV_AUDIENCE,
        ),
        # Never connected: building the document touches no table.
        session_factory=sessionmaker(create_engine("postgresql+psycopg://")),
        check_renderer=False,
    )
    schema = app.openapi()
    schema.setdefault("components", {})["securitySchemes"] = {
        "bearer": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path, operations in schema["paths"].items():
        for operation in operations.values():
            operation["security"] = [] if path == "/healthz" else [{"bearer": []}]
            # Errors are served as application/problem+json only; say so, with the schema.
            for response in operation["responses"].values():
                content = response.get("content", {})
                if PROBLEM_MEDIA_TYPE in content and "application/json" in content:
                    content[PROBLEM_MEDIA_TYPE] = content.pop("application/json")
    return schema


def render() -> str:
    return json.dumps(document(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m qlab.api.openapi", description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare, do not write")
    args = parser.parse_args(argv)
    text = render()
    if args.check:
        if not OPENAPI_FILE.is_file() or OPENAPI_FILE.read_text(encoding="utf-8") != text:
            print(
                "apps/api/openapi.json is out of date. Run `python -m qlab.api.openapi` and "
                "regenerate the client.",
                file=sys.stderr,
            )
            return 1
        print("apps/api/openapi.json is current.")
        return 0
    OPENAPI_FILE.write_text(text, encoding="utf-8")
    print(f"Wrote {OPENAPI_FILE}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
