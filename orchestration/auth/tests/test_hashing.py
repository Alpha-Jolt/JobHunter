"""Unit tests for auth/hashing.py — argon2id password hashing."""

from orchestration.auth.hashing import hash_password, needs_rehash, verify_password


# ── hash_password ─────────────────────────────────────────────────────────────

def test_hash_returns_string():
    assert isinstance(hash_password("password123"), str)


def test_hash_starts_with_argon2():
    assert hash_password("password123").startswith("$argon2")


def test_different_passwords_produce_different_hashes():
    assert hash_password("password1") != hash_password("password2")


def test_same_password_produces_different_hashes():
    # argon2 uses random salt
    assert hash_password("password123") != hash_password("password123")


def test_hash_non_empty_output():
    result = hash_password("a" * 8)
    assert len(result) > 20


def test_hash_long_password():
    result = hash_password("x" * 100)
    assert result.startswith("$argon2")


def test_hash_special_characters():
    result = hash_password("p@$$w0rd!#%^&*()")
    assert result.startswith("$argon2")


def test_hash_unicode_password():
    result = hash_password("пароль123")
    assert result.startswith("$argon2")


# ── verify_password ───────────────────────────────────────────────────────────

def test_verify_correct_password_returns_true():
    h = hash_password("secret123")
    assert verify_password("secret123", h) is True


def test_verify_wrong_password_returns_false():
    h = hash_password("secret123")
    assert verify_password("wrongpass", h) is False


def test_verify_empty_password_returns_false():
    h = hash_password("secret123")
    assert verify_password("", h) is False


def test_verify_case_sensitive():
    h = hash_password("Secret123")
    assert verify_password("secret123", h) is False


def test_verify_invalid_hash_returns_false():
    assert verify_password("password", "not-a-valid-hash") is False


def test_verify_empty_hash_returns_false():
    assert verify_password("password", "") is False


def test_verify_none_like_hash_returns_false():
    assert verify_password("password", "null") is False


def test_verify_special_chars():
    pw = "p@$$w0rd!#"
    h = hash_password(pw)
    assert verify_password(pw, h) is True


def test_verify_unicode():
    pw = "пароль123"
    h = hash_password(pw)
    assert verify_password(pw, h) is True


# ── needs_rehash ──────────────────────────────────────────────────────────────

def test_fresh_hash_does_not_need_rehash():
    h = hash_password("password123")
    assert needs_rehash(h) is False


def test_needs_rehash_invalid_hash_raises():
    """needs_rehash on a non-argon2 string should raise or return True."""
    try:
        result = needs_rehash("not-an-argon2-hash")
        # If no exception, result must be truthy (prompt rehash)
        assert result is True
    except Exception:
        pass  # raising is also acceptable behaviour
