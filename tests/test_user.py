import pytest

from core.security import verify_password
from database import session as SessionLocal
from models.user import User

USERS = "/users/"

VALID_USER = {
    "username": "manager1",
    "password": "Str0ng-Passw0rd!",
    "email": "manager1@example.com",
    "role": "manager",
    "first_name": "Nasha",
    "last_name": "Pretty",
}


def _stored_hash(username):
    with SessionLocal() as db:
        return db.query(User).filter(User.username == username).one().password_hash


def _login(client, username, password):
    return client.post("/auth/login", data={"username": username, "password": password})


def test_create_user(client):
    response = client.post(USERS, json=VALID_USER)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["username"] == "manager1"
    assert body["email"] == "manager1@example.com"
    assert body["role"] == "manager"
    assert body["first_name"] == "Nasha"
    assert body["created_at"]


def test_create_user_without_names(client):
    payload = {k: v for k, v in VALID_USER.items() if k not in ("first_name", "last_name")}

    response = client.post(USERS, json=payload)

    assert response.status_code == 201
    assert response.json()["first_name"] is None
    assert response.json()["last_name"] is None


def test_create_user_never_returns_the_password(client):
    body = client.post(USERS, json=VALID_USER).json()

    assert "password" not in body
    assert "password_hash" not in body


def test_create_user_stores_a_hashed_password(client):
    client.post(USERS, json=VALID_USER)

    stored = _stored_hash("manager1")

    assert stored != VALID_USER["password"]
    assert verify_password(VALID_USER["password"], stored)


def test_user_created_through_the_users_endpoint_can_log_in(client):
    client.post(USERS, json=VALID_USER)

    response = _login(client, "manager1", VALID_USER["password"])

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_list_users(client, make_user):
    made = [make_user(), make_user()]

    response = client.get(USERS)

    assert response.status_code == 200
    assert {u["id"] for u in response.json()} == {u["id"] for u in made}


def test_get_user_by_id(client, make_user):
    user = make_user(username="findme")

    response = client.get(f"{USERS}{user['id']}")

    assert response.status_code == 200
    assert response.json()["username"] == "findme"


def test_update_user(client, make_user):
    user = make_user()

    response = client.put(
        f"{USERS}{user['id']}",
        json={"role": "admin", "first_name": "Renamed"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "admin"
    assert body["first_name"] == "Renamed"
    assert body["username"] == user["username"]


def test_update_user_password_replaces_the_hash(client):
    user = client.post(USERS, json=VALID_USER).json()

    response = client.put(f"{USERS}{user['id']}", json={"password": "Brand-new-pass1"})

    assert response.status_code == 200
    assert _login(client, "manager1", "Brand-new-pass1").status_code == 200
    assert _login(client, "manager1", VALID_USER["password"]).status_code == 401


def test_delete_user(client, make_user):
    user = make_user()
    url = f"{USERS}{user['id']}"

    response = client.delete(url)

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(url).status_code == 404


@pytest.mark.parametrize("missing", ["username", "password", "email", "role"])
def test_create_user_missing_required_field_returns_422(client, missing):
    payload = {k: v for k, v in VALID_USER.items() if k != missing}

    response = client.post(USERS, json=payload)

    assert response.status_code == 422


def test_create_user_with_invalid_email_returns_422(client):
    response = client.post(USERS, json={**VALID_USER, "email": "definitely-not-an-email"})

    assert response.status_code == 422


def test_update_user_with_invalid_email_returns_422(client, make_user):
    user = make_user()

    response = client.put(f"{USERS}{user['id']}", json={"email": "nope"})

    assert response.status_code == 422


def test_duplicate_username_returns_409(client, make_user):
    existing = make_user()

    response = client.post(
        USERS,
        json={**VALID_USER, "username": existing["username"]},
    )

    assert response.status_code == 409


def test_update_to_an_existing_username_returns_409(client, make_user):
    first = make_user()
    second = make_user()

    response = client.put(f"{USERS}{second['id']}", json={"username": first["username"]})

    assert response.status_code == 409


def test_cannot_delete_user_who_has_recorded_sales(client, make_user, make_sale):
    cashier = make_user()
    make_sale(user_id=cashier["id"])

    response = client.delete(f"{USERS}{cashier['id']}")

    assert response.status_code == 409
    assert client.get(f"{USERS}{cashier['id']}").status_code == 200