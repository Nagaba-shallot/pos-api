from decimal import Decimal

import pytest

SALES = "/sales/"
SALE_DATE = "2026-09-20T10:00:00"


def money(value):
    return Decimal(str(value))


def sale_payload(customer_id, user_id, **overrides):
    payload = {
        "customer_id": customer_id,
        "user_id": user_id,
        "sale_date": SALE_DATE,
        "total_amount": "116.00",
        "tax_amount": "16.00",
        "discount_amount": "5.00",
    }
    payload.update(overrides)
    return payload


def test_create_sale(client, make_customer, make_user):
    customer = make_customer()
    cashier = make_user()

    response = client.post(SALES, json=sale_payload(customer["customer_id"], cashier["id"]))

    assert response.status_code == 201
    body = response.json()
    assert body["sale_id"] > 0
    assert body["customer_id"] == customer["customer_id"]
    assert body["user_id"] == cashier["id"]
    assert body["sale_date"].startswith("2026-09-20T10:00:00")
    assert money(body["total_amount"]) == Decimal("116.00")
    assert money(body["tax_amount"]) == Decimal("16.00")
    assert money(body["discount_amount"]) == Decimal("5.00")


def test_list_sales(client, make_sale):
    made = [make_sale(), make_sale()]

    response = client.get(SALES)

    assert response.status_code == 200
    assert {s["sale_id"] for s in response.json()} == {s["sale_id"] for s in made}


def test_get_sale_by_id(client, make_sale):
    sale = make_sale()

    response = client.get(f"{SALES}{sale['sale_id']}")

    assert response.status_code == 200
    assert response.json()["sale_id"] == sale["sale_id"]


def test_update_sale(client, make_sale):
    sale = make_sale()

    response = client.put(
        f"{SALES}{sale['sale_id']}",
        json={"total_amount": "250.50", "discount_amount": "10.00"},
    )

    assert response.status_code == 200
    body = response.json()
    assert money(body["total_amount"]) == Decimal("250.50")
    assert money(body["discount_amount"]) == Decimal("10.00")
    assert body["customer_id"] == sale["customer_id"]
    assert money(body["tax_amount"]) == money(sale["tax_amount"])


def test_delete_sale(client, make_sale):
    sale = make_sale()
    url = f"{SALES}{sale['sale_id']}"

    response = client.delete(url)

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(url).status_code == 404


@pytest.mark.parametrize(
    "missing",
    ["customer_id", "user_id", "sale_date", "total_amount", "tax_amount", "discount_amount"],
)
def test_create_sale_missing_required_field_returns_422(
    client, make_customer, make_user, missing
):
    payload = sale_payload(make_customer()["customer_id"], make_user()["id"])
    del payload[missing]

    response = client.post(SALES, json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field, bad_value",
    [
        ("sale_date", "yesterday-ish"),
        ("total_amount", "a lot"),
        ("tax_amount", "tax"),
        ("customer_id", "abc"),
    ],
)
def test_create_sale_with_invalid_value_returns_422(
    client, make_customer, make_user, field, bad_value
):
    payload = sale_payload(make_customer()["customer_id"], make_user()["id"])
    payload[field] = bad_value

    response = client.post(SALES, json=payload)

    assert response.status_code == 422


def test_create_sale_for_unknown_customer_returns_409(client, make_user):
    response = client.post(SALES, json=sale_payload(99999, make_user()["id"]))

    assert response.status_code == 409


def test_create_sale_for_unknown_user_returns_409(client, make_customer):
    response = client.post(SALES, json=sale_payload(make_customer()["customer_id"], 99999))

    assert response.status_code == 409


def test_update_sale_to_unknown_customer_returns_409(client, make_sale):
    sale = make_sale()

    response = client.put(f"{SALES}{sale['sale_id']}", json={"customer_id": 99999})

    assert response.status_code == 409


def test_cannot_delete_sale_that_has_items(client, make_sale, make_sale_item):
    sale = make_sale()
    make_sale_item(sale_id=sale["sale_id"])

    response = client.delete(f"{SALES}{sale['sale_id']}")

    assert response.status_code == 409
    assert client.get(f"{SALES}{sale['sale_id']}").status_code == 200