from decimal import Decimal

import pytest

PAYMENTS = "/payments/"
PAYMENT_DATE = "2026-09-20T10:05:00"


def money(value):
    return Decimal(str(value))


def payment_payload(sale_id, **overrides):
    payload = {
        "sale_id": sale_id,
        "payment_method": "card",
        "payment_amount": "116.00",
        "payment_date": PAYMENT_DATE,
    }
    payload.update(overrides)
    return payload


def test_create_payment(client, make_sale):
    sale = make_sale()

    response = client.post(PAYMENTS, json=payment_payload(sale["sale_id"]))

    assert response.status_code == 201
    body = response.json()
    assert body["payment_id"] > 0
    assert body["sale_id"] == sale["sale_id"]
    assert body["payment_method"] == "card"
    assert money(body["payment_amount"]) == Decimal("116.00")
    assert body["payment_date"].startswith("2026-09-20T10:05:00")


def test_a_sale_can_be_paid_in_several_payments(client, make_sale):
    sale = make_sale()

    for method in ("cash", "mobile"):
        response = client.post(
            PAYMENTS,
            json=payment_payload(sale["sale_id"], payment_method=method, payment_amount="58.00"),
        )
        assert response.status_code == 201

    assert len(client.get(PAYMENTS).json()) == 2


def test_list_payments(client, make_payment):
    made = [make_payment(), make_payment()]

    response = client.get(PAYMENTS)

    assert response.status_code == 200
    assert {p["payment_id"] for p in response.json()} == {p["payment_id"] for p in made}


def test_get_payment_by_id(client, make_payment):
    payment = make_payment(payment_method="mobile")

    response = client.get(f"{PAYMENTS}{payment['payment_id']}")

    assert response.status_code == 200
    assert response.json()["payment_method"] == "mobile"


def test_update_payment(client, make_payment):
    payment = make_payment(payment_method="cash", payment_amount="50.00")

    response = client.put(
        f"{PAYMENTS}{payment['payment_id']}",
        json={"payment_method": "card", "payment_amount": "75.25"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["payment_method"] == "card"
    assert money(body["payment_amount"]) == Decimal("75.25")
    assert body["sale_id"] == payment["sale_id"]


def test_delete_payment(client, make_payment):
    payment = make_payment()
    url = f"{PAYMENTS}{payment['payment_id']}"

    response = client.delete(url)

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(url).status_code == 404


@pytest.mark.parametrize(
    "missing", ["sale_id", "payment_method", "payment_amount", "payment_date"]
)
def test_create_payment_missing_required_field_returns_422(client, make_sale, missing):
    payload = payment_payload(make_sale()["sale_id"])
    del payload[missing]

    response = client.post(PAYMENTS, json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field, bad_value",
    [
        ("payment_amount", "lots"),
        ("payment_date", "not-a-date"),
        ("sale_id", "abc"),
        ("payment_method", None),
    ],
)
def test_create_payment_with_invalid_value_returns_422(client, make_sale, field, bad_value):
    payload = payment_payload(make_sale()["sale_id"])
    payload[field] = bad_value

    response = client.post(PAYMENTS, json=payload)

    assert response.status_code == 422


def test_create_payment_for_unknown_sale_returns_409(client):
    response = client.post(PAYMENTS, json=payment_payload(99999))

    assert response.status_code == 409


def test_update_payment_to_unknown_sale_returns_409(client, make_payment):
    payment = make_payment()

    response = client.put(f"{PAYMENTS}{payment['payment_id']}", json={"sale_id": 99999})

    assert response.status_code == 409


def test_cannot_delete_sale_that_has_payments(client, make_sale, make_payment):
    sale = make_sale()
    make_payment(sale_id=sale["sale_id"])

    response = client.delete(f"/sales/{sale['sale_id']}")

    assert response.status_code == 409