from datetime import datetime, timedelta, timezone

import jwt
import pytest

from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    jwt_algorithm,
    jwt_secret,
    verify_password,
)


def test_hash_password_does_not_return_plain_text():
    password = "mysecretpassword"
    hashed = hash_password(password)

    assert isinstance(hashed, str)
    assert hashed != password


def test_hashing_the_same_password_twice_gives_different_hashes():
    assert hash_password("same-password") != hash_password("same-password")


def test_verify_password_accepts_the_correct_password():
    hashed = hash_password("correct horse")

    assert verify_password("correct horse", hashed) is True


def test_verify_password_rejects_a_wrong_password():
    hashed = hash_password("correct horse")

    assert verify_password("wrong horse", hashed) is False


def test_access_token_round_trip():
    token = create_access_token(42)
    payload = decode_access_token(token)

    assert payload["sub"] == "42"
    assert "exp" in payload


def test_access_token_expires_in_the_future():
    payload = decode_access_token(create_access_token(1))

    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert expires_at > datetime.now(timezone.utc)


def test_expired_token_is_rejected():
    expired = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        jwt_secret,
        algorithm=jwt_algorithm,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired)


def test_token_signed_with_another_secret_is_rejected():
    forged = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "x" * 64,
        algorithm=jwt_algorithm,
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(forged)


def test_garbage_token_is_rejected():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("not-a-jwt")