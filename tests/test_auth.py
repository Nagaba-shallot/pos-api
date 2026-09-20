from datetime import datetime, timedelta, timezone

import jwt
import pytest

from core.security import (
    create_access_token,
    jwt_algorithm,
    jwt_secret,
    verify_password,
)
from database import session as SessionLocal
from models.user import User

PROTECTED_URL = "/products/"


def _token(sub, secret=jwt_secret, expires_in=timedelta(minutes=5), **extra):
    payload = {"exp": datetime.now(timezone.utc) + expires_in, **extra}
    if sub is not None:
        payload["sub"] = sub
    return jwt.encode(payload, secret, algorithm=jwt_algorithm)


def _bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_register_creates_a_user(client, auth_user_data):
    response = client.post("/auth/register", json=auth_user_data)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["username"] == auth_user_data["username"]
    assert body["email"] == auth_user_data["email"]
    assert body["role"] == auth_user_data["role"]


def test_register_never_returns_the_password(client, auth_user_data):
    body = client.post("/auth/register", json=auth_user_data).json()

    assert "password" not in body
    assert "password_hash" not in body


def test_register_stores_a_hashed_password(client, auth_user_data):
    client.post("/auth/register", json=auth_user_data)

    with SessionLocal() as db:
        user = db.query(User).filter(User.username == auth_user_data["username"]).one()
        stored = user.password_hash

    assert stored != auth_user_data["password"]
    assert verify_password(auth_user_data["password"], stored)


def test_register_duplicate_username_is_rejected(client, auth_user_data):
    client.post("/auth/register", json=auth_user_data)
    duplicate = {**auth_user_data, "email": "different@example.com"}

    response = client.post("/auth/register", json=duplicate)

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_register_duplicate_email_is_rejected(client, auth_user_data):
    client.post("/auth/register", json=auth_user_data)
    duplicate = {**auth_user_data, "username": "someone-else"}

    response = client.post("/auth/register", json=duplicate)

    assert response.status_code == 400
    assert "registered" in response.json()["detail"]


def test_register_with_invalid_email_returns_422(client, auth_user_data):
    response = client.post(
        "/auth/register", json={**auth_user_data, "email": "not-an-email"}
    )

    assert response.status_code == 422


@pytest.mark.parametrize("missing", ["username", "password", "email", "role"])
def test_register_missing_required_field_returns_422(client, auth_user_data, missing):
    payload = {k: v for k, v in auth_user_data.items() if k != missing}

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 422



def test_login_returns_a_bearer_token(client, auth_user_data):
    client.post("/auth/register", json=auth_user_data)

    response = client.post(
        "/auth/login",
        data={
            "username": auth_user_data["username"],
            "password": auth_user_data["password"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_wrong_password_returns_401(client, auth_user_data):
    client.post("/auth/register", json=auth_user_data)

    response = client.post(
        "/auth/login",
        data={"username": auth_user_data["username"], "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_with_unknown_user_returns_401(client):
    response = client.post(
        "/auth/login", data={"username": "nobody", "password": "whatever"}
    )

    assert response.status_code == 401


@pytest.mark.parametrize("payload", [{}, {"username": "only-a-username"}, {"password": "only-a-password"}])
def test_login_with_incomplete_form_returns_422(client, payload):
    response = client.post("/auth/login", data=payload)

    assert response.status_code == 422


def test_valid_token_grants_access(client, auth_headers):
    response = client.get(PROTECTED_URL, headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_token_created_for_a_registered_user_grants_access(client, auth_user_data):
    user = client.post("/auth/register", json=auth_user_data).json()

    response = client.get(PROTECTED_URL, headers=_bearer(create_access_token(user["id"])))

    assert response.status_code == 200


def test_missing_token_returns_401(client):
    assert client.get(PROTECTED_URL).status_code == 401


def test_non_bearer_scheme_returns_401(client):
    response = client.get(PROTECTED_URL, headers={"Authorization": "Basic YTpi"})

    assert response.status_code == 401


@pytest.mark.parametrize(
    "token",
    [
        pytest.param("not-a-jwt", id="garbage"),
        pytest.param(_token("1", expires_in=timedelta(minutes=-5)), id="expired"),
        pytest.param(_token("1", secret="x" * 64), id="wrong-secret"),
        pytest.param(_token(None), id="no-subject"),
        pytest.param(_token("abc"), id="non-numeric-subject"),
        pytest.param(_token("0"), id="zero-subject"),
        pytest.param(_token("-5"), id="negative-subject"),
        pytest.param(_token("99999"), id="user-does-not-exist"),
    ],
)
def test_invalid_tokens_are_rejected(client, token):
    response = client.get(PROTECTED_URL, headers=_bearer(token))

    assert response.status_code == 401


def test_token_stops_working_when_the_user_is_deleted(client, auth_user_data):
    user = client.post("/auth/register", json=auth_user_data).json()
    headers = _bearer(create_access_token(user["id"]))
    assert client.get(PROTECTED_URL, headers=headers).status_code == 200

    assert client.delete(f"/users/{user['id']}").status_code == 204

    assert client.get(PROTECTED_URL, headers=headers).status_code == 401