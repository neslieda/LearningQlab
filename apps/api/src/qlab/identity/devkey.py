"""The local development signing key (D-59).

The key is generated on the developer's machine and kept outside the repository, readable by
its owner only. It signs the tokens of the local development accounts and nothing else.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

DEV_KEY_FILE_ENV = "QLAB_DEV_KEY_FILE"


class DevKeyError(Exception):
    """The development key file is missing, unsafe or not a key."""


def default_path() -> Path:
    """`QLAB_DEV_KEY_FILE`, or `~/.qlab/dev-signing-key.pem`."""
    configured = os.environ.get(DEV_KEY_FILE_ENV)
    return Path(configured) if configured else Path.home() / ".qlab" / "dev-signing-key.pem"


def generate(path: Path) -> Ed25519PrivateKey:
    """Create a new key at `path` (mode 0600; the directory 0700 if it is created). An
    existing file is never overwritten: DevKeyError."""
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    key = Ed25519PrivateKey.generate()
    encoded = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise DevKeyError(f"{path} already exists; it is not overwritten") from None
    with os.fdopen(descriptor, "wb") as file:
        file.write(encoded)
    return key


def load(path: Path) -> Ed25519PrivateKey:
    """The key stored at `path`. DevKeyError when the file is missing, is readable by anyone
    but its owner, or does not hold an Ed25519 private key."""
    try:
        mode = path.stat().st_mode
    except FileNotFoundError:
        raise DevKeyError(f"{path} does not exist") from None
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise DevKeyError(f"{path} is accessible to other users; expected mode 0600")
    try:
        key = serialization.load_pem_private_key(path.read_bytes(), password=None)
    except ValueError, TypeError:
        raise DevKeyError(f"{path} does not hold a private key") from None
    if not isinstance(key, Ed25519PrivateKey):
        raise DevKeyError(f"{path} does not hold an Ed25519 key")
    return key
