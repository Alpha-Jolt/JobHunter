"""Password hashing using argon2id via argon2-cffi."""

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError, InvalidHashError

_ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,   # 64 MB
    parallelism=2,
    hash_len=32,
    salt_len=16,
)


def hash_password(plain: str) -> str:
    """Hash a plaintext password with argon2id.

    Args:
        plain: Plaintext password (min 8 chars enforced at service layer).

    Returns:
        Argon2id hash string.
    """
    return _ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify plaintext against an argon2id hash.

    Args:
        plain: Plaintext candidate.
        hashed: Stored argon2id hash.

    Returns:
        True if password matches, False otherwise.
    """
    try:
        return _ph.verify(hashed, plain)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(hashed: str) -> bool:
    """Check if a hash needs to be rehashed (e.g., params changed).

    Args:
        hashed: Stored argon2id hash.

    Returns:
        True if rehash is recommended.
    """
    return _ph.check_needs_rehash(hashed)
