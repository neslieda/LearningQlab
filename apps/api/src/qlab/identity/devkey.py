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
    """The key stored at `path`. DevKeyError when the file is missing, is a symbolic link or
    not a regular file, belongs to another user, is accessible to anyone but its owner, or
    does not hold an Ed25519 private key."""
    try:
        # Non-blocking, so that a named pipe put in its place cannot hang the caller.
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        raise DevKeyError(f"{path} does not exist") from None
    except OSError:
        raise DevKeyError(f"{path} cannot be opened (a symbolic link is refused)") from None
    # Checked on the open descriptor, so what is checked is what is read.
    status = os.fstat(descriptor)
    if not stat.S_ISREG(status.st_mode):
        os.close(descriptor)
        raise DevKeyError(f"{path} is not a regular file")
    with os.fdopen(descriptor, "rb") as file:
        if status.st_uid != os.getuid():
            raise DevKeyError(f"{path} belongs to another user")
        if status.st_mode & (stat.S_IRWXG | stat.S_IRWXO):
            raise DevKeyError(f"{path} is accessible to other users; expected mode 0600")
        encoded = file.read(16 * 1024)
    try:
        key = serialization.load_pem_private_key(encoded, password=None)
    except ValueError, TypeError:
        raise DevKeyError(f"{path} does not hold a private key") from None
    if not isinstance(key, Ed25519PrivateKey):
        raise DevKeyError(f"{path} does not hold an Ed25519 key")
    return key
