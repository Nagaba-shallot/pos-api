import pytest

CUSTOMERS = "/customers/"

VALID_CUSTOMER = {
    "first_name": "Grass",
    "last_name": "Hopper",
    "email": "grace@example.com",
    "phone_number": "0722000111",
    "address": "10 Navy Yard",
}


def test_create_customer(client):
    response = client.post(CUSTOMERS, json=VALID_CUSTOMER)

    assert response.status_code == 201
    body = response.json()
    assert body["customer_id"] > 0
    for field, value in VALID_CUSTOMER.items():
        assert body[field] == value
    assert body["created_at"]
    assert body["updated_at"]


def test_create_customer_with_only_required_fields(client):
    response = client.post(
        CUSTOMERS,
        json={"first_name": "Al", "last_name": "Turing", "email": "al@example.com"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["phone_number"] is None
    assert body["address"] is None


def test_customers_without_phone_numbers_can_coexist(client):
    for n in range(2):
        response = client.post(
            CUSTOMERS,
            json={"first_name": "No", "last_name": "Phone", "email": f"nophone{n}@example.com"},
        )
        assert response.status_code == 201


def test_list_customers(client, make_customer):
    made = [make_customer(), make_customer()]

    response = client.get(CUSTOMERS)

    assert response.status_code == 200
    assert {c["customer_id"] for c in response.json()} == {c["customer_id"] for c in made}


def test_get_customer_by_id(client, make_customer):
    customer = make_customer(first_name="Linus")

    response = client.get(f"{CUSTOMERS}{customer['customer_id']}")

    assert response.status_code == 200
    assert response.json()["first_name"] == "Linus"


def test_update_customer(client, make_customer):
    customer = make_customer()

    response = client.put(
        f"{CUSTOMERS}{customer['customer_id']}",
        json={"first_name": "Updated", "address": "New Street"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == "Updated"
    assert body["address"] == "New Street"
    assert body["last_name"] == customer["last_name"]
    assert body["email"] == customer["email"]


def test_delete_customer(client, make_customer):
    customer = make_customer()
    url = f"{CUSTOMERS}{customer['customer_id']}"

    response = client.delete(url)

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(url).status_code == 404


@pytest.mark.parametrize("missing", ["first_name", "last_name", "email"])
def test_create_customer_missing_required_field_returns_422(client, missing):
    payload = {k: v for k, v in VALID_CUSTOMER.items() if k != missing}

    response = client.post(CUSTOMERS, json=payload)

    assert response.status_code == 422


def test_create_customer_with_wrong_type_returns_422(client):
    response = client.post(CUSTOMERS, json={**VALID_CUSTOMER, "first_name": {"a": 1}})

    assert response.status_code == 422


def test_duplicate_email_returns_409(client, make_customer):
    existing = make_customer()

    response = client.post(
        CUSTOMERS,
        json={**VALID_CUSTOMER, "email": existing["email"]},
    )

    assert response.status_code == 409


def test_duplicate_phone_number_returns_409(client, make_customer):
    existing = make_customer()

    response = client.post(
        CUSTOMERS,
        json={**VALID_CUSTOMER, "phone_number": existing["phone_number"]},
    )

    assert response.status_code == 409


def test_update_to_an_existing_email_returns_409(client, make_customer):
    first = make_customer()
    second = make_customer()

    response = client.put(
        f"{CUSTOMERS}{second['customer_id']}", json={"email": first["email"]}
    )

    assert response.status_code == 409


def test_cannot_delete_customer_with_sales(client, make_customer, make_sale):
    customer = make_customer()
    make_sale(customer_id=customer["customer_id"])

    response = client.delete(f"{CUSTOMERS}{customer['customer_id']}")

    assert response.status_code == 409
    assert client.get(f"{CUSTOMERS}{customer['customer_id']}").status_code == 200