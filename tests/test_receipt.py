import re
from datetime import datetime

import pytest

RECEIPTS = "/receipts/"
PRINTED_TIME = "2026-09-20T10:15:00"


def receipt_payload(sale_id, **overrides):
    payload = {
        "sale_id": sale_id,
        "receipt_text": "Thanks for shopping!",
        "printed_time": PRINTED_TIME,
    }
    payload.update(overrides)
    return payload


def test_create_receipt(client, make_sale):
    sale = make_sale()

    response = client.post(RECEIPTS, json=receipt_payload(sale["sale_id"]))

    assert response.status_code == 201
    body = response.json()
    assert body["receipt_id"] > 0
    assert body["sale_id"] == sale["sale_id"]
    assert body["receipt_text"] == "Thanks for shopping!"
    assert datetime.fromisoformat(body["printed_time"]) == datetime(2026, 9, 20, 10, 15)


def test_receipt_number_is_generated(client, make_sale):
    response = client.post(RECEIPTS, json=receipt_payload(make_sale()["sale_id"]))

    assert re.fullmatch(r"REC-[0-9A-F]{8}", response.json()["receipt_number"])


def test_receipt_number_supplied_by_the_client_is_ignored(client, make_sale):
    response = client.post(
        RECEIPTS,
        json=receipt_payload(make_sale()["sale_id"], receipt_number="MY-OWN-NUMBER"),
    )

    assert response.status_code == 201
    assert response.json()["receipt_number"] != "MY-OWN-NUMBER"


def test_receipt_numbers_are_unique(client, make_receipt):
    numbers = {make_receipt()["receipt_number"] for _ in range(5)}

    assert len(numbers) == 5


def test_receipt_text_is_optional(client, make_sale):
    response = client.post(
        RECEIPTS,
        json={"sale_id": make_sale()["sale_id"], "printed_time": PRINTED_TIME},
    )

    assert response.status_code == 201
    assert response.json()["receipt_text"] is None


def test_list_receipts(client, make_receipt):
    made = [make_receipt(), make_receipt()]

    response = client.get(RECEIPTS)

    assert response.status_code == 200
    assert {r["receipt_id"] for r in response.json()} == {r["receipt_id"] for r in made}


def test_get_receipt_by_id(client, make_receipt):
    receipt = make_receipt()

    response = client.get(f"{RECEIPTS}{receipt['receipt_id']}")

    assert response.status_code == 200
    assert response.json()["receipt_number"] == receipt["receipt_number"]


def test_update_receipt_text(client, make_receipt):
    receipt = make_receipt()

    response = client.put(
        f"{RECEIPTS}{receipt['receipt_id']}", json={"receipt_text": "Corrected text"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["receipt_text"] == "Corrected text"
    assert body["receipt_number"] == receipt["receipt_number"]


def test_update_receipt_printed_time(client, make_receipt):
    receipt = make_receipt()

    response = client.put(
        f"{RECEIPTS}{receipt['receipt_id']}", json={"printed_time": "2026-10-01T08:30:00"}
    )

    assert response.status_code == 200
    assert datetime.fromisoformat(response.json()["printed_time"]) == datetime(
        2026, 10, 1, 8, 30
    )


def test_delete_receipt(client, make_receipt):
    receipt = make_receipt()
    url = f"{RECEIPTS}{receipt['receipt_id']}"

    response = client.delete(url)

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(url).status_code == 404


@pytest.mark.parametrize("missing", ["sale_id", "printed_time"])
def test_create_receipt_missing_required_field_returns_422(client, make_sale, missing):
    payload = receipt_payload(make_sale()["sale_id"])
    del payload[missing]

    response = client.post(RECEIPTS, json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field, bad_value",
    [("printed_time", "not-a-date"), ("sale_id", "abc"), ("receipt_text", ["list"])],
)
def test_create_receipt_with_invalid_value_returns_422(client, make_sale, field, bad_value):
    payload = receipt_payload(make_sale()["sale_id"])
    payload[field] = bad_value

    response = client.post(RECEIPTS, json=payload)

    assert response.status_code == 422


def test_create_receipt_for_unknown_sale_returns_409(client):
    response = client.post(RECEIPTS, json=receipt_payload(99999))

    assert response.status_code == 409


def test_update_receipt_to_unknown_sale_returns_409(client, make_receipt):
    receipt = make_receipt()

    response = client.put(f"{RECEIPTS}{receipt['receipt_id']}", json={"sale_id": 99999})

    assert response.status_code == 409


def test_update_receipt_to_a_duplicate_number_returns_409(client, make_receipt):
    first = make_receipt()
    second = make_receipt()

    response = client.put(
        f"{RECEIPTS}{second['receipt_id']}",
        json={"receipt_number": first["receipt_number"]},
    )

    assert response.status_code == 409