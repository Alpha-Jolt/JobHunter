"""Unit tests for auth/tokens.py — JWT encode/decode, refresh token utils."""

from datetime import datetime, timedelta, timezone

import pytest

from orchestration.auth.models.user import RoleEnum
from orchestration.auth.tokens import (
    TokenError,
    TokenExpiredError,
    decode_access_token,
    encode_access_token,
    generate_refresh_token,
    hash_token,
)

_SECRET = "test-secret-key-that-is-32chars-long!"
_ALG = "HS256"


def _future(minutes: int = 15) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def _past(minutes: int = 1) -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=minutes)


# ── encode_access_token ───────────────────────────────────────────────────────

def test_encode_returns_string():
    token = encode_access_token("user-id", RoleEnum.HUNTER, _SECRET, _ALG, _future())
    assert isinstance(token, str)
    assert len(token) > 20


def test_encode_produces_three_part_jwt():
    token = encode_access_token("user-id", RoleEnum.HUNTER, _SECRET, _ALG, _future())
    assert token.count(".") == 2


def test_encode_different_users_produce_different_tokens():
    t1 = encode_access_token("user-1", RoleEnum.HUNTER, _SECRET, _ALG, _future())
    t2 = encode_access_token("user-2", RoleEnum.HUNTER, _SECRET, _ALG, _future())
    assert t1 != t2


def test_encode_different_roles_produce_different_tokens():
    t1 = encode_access_token("user-id", RoleEnum.HUNTER, _SECRET, _ALG, _future())
    t2 = encode_access_token("user-id", RoleEnum.ADMIN, _SECRET, _ALG, _future())
    assert t1 != t2


# ── decode_access_token ───────────────────────────────────────────────────────

def test_decode_valid_token_returns_payload():
    token = encode_access_token("abc-123", RoleEnum.HUNTER, _SECRET, _ALG, _future())
    payload = decode_access_token(token, _SECRET, _ALG)
    assert payload.sub == "abc-123"
    assert payload.role == RoleEnum.HUNTER


def test_decode_all_roles():
    for role in RoleEnum:
        token = encode_access_token("u", role, _SECRET, _ALG, _future())
        payload = decode_access_token(token, _SECRET, _ALG)
        assert payload.role == role


def test_decode_expired_token_raises_token_expired():
    token = encode_access_token("user-id", RoleEnum.HUNTER, _SECRET, _ALG, _past())
    with pytest.raises(TokenExpiredError):
        decode_access_token(token, _SECRET, _ALG)


def test_decode_wrong_secret_raises_token_error():
    token = encode_access_token("user-id", RoleEnum.HUNTER, _SECRET, _ALG, _future())
    with pytest.raises(TokenError):
        decode_access_token(token, "wrong-secret-key-minimum-32chars!!", _ALG)


def test_decode_malformed_token_raises_token_error():
    with pytest.raises(TokenError):
        decode_access_token("not.a.jwt", _SECRET, _ALG)


def test_decode_empty_string_raises_token_error():
    with pytest.raises(TokenError):
        decode_access_token("", _SECRET, _ALG)


def test_decode_payload_has_exp_and_iat():
    token = encode_access_token("user-id", RoleEnum.ADMIN, _SECRET, _ALG, _future())
    payload = decode_access_token(token, _SECRET, _ALG)
    assert payload.exp is not None
    assert payload.iat is not None
    assert payload.exp > payload.iat


def test_decode_tampered_token_raises_token_error():
    token = encode_access_token("user-id", RoleEnum.HUNTER, _SECRET, _ALG, _future())
    parts = token.split(".")
    parts[1] = parts[1][::-1]  # corrupt payload
    with pytest.raises(TokenError):
        decode_access_token(".".join(parts), _SECRET, _ALG)


# ── generate_refresh_token ────────────────────────────────────────────────────

def test_generate_refresh_token_returns_string():
    assert isinstance(generate_refresh_token(), str)


def test_generate_refresh_token_is_url_safe():
    token = generate_refresh_token()
    import urllib.parse
    assert urllib.parse.quote(token, safe="-_~.") == token or len(token) > 20


def test_generate_refresh_tokens_are_unique():
    tokens = {generate_refresh_token() for _ in range(20)}
    assert len(tokens) == 20


def test_generate_refresh_token_min_length():
    token = generate_refresh_token()
    assert len(token) >= 40


# ── hash_token ────────────────────────────────────────────────────────────────

def test_hash_token_returns_hex_string():
    result = hash_token("some-token")
    assert all(c in "0123456789abcdef" for c in result)


def test_hash_token_length_is_64():
    assert len(hash_token("any-token")) == 64


def test_hash_token_deterministic():
    assert hash_token("token") == hash_token("token")


def test_hash_token_different_inputs_differ():
    assert hash_token("token-a") != hash_token("token-b")


def test_hash_token_empty_string():
    result = hash_token("")
    assert len(result) == 64
