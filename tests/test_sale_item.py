from decimal import Decimal

import pytest

SALE_ITEMS = "/sale-items/"


def money(value):
    return Decimal(str(value))


def item_payload(sale_id, product_id, **overrides):
    payload = {
        "sale_id": sale_id,
        "product_id": product_id,
        "quantity": 3,
        "unit_price": "10.00",
        "discount_amount": "5.00",
        "subtotal": "25.00",
    }
    payload.update(overrides)
    return payload


def test_create_sale_item(client, make_sale, make_product):
    sale = make_sale()
    product = make_product()

    response = client.post(
        SALE_ITEMS, json=item_payload(sale["sale_id"], product["product_id"])
    )

    assert response.status_code == 201
    body = response.json()
    assert body["sale_item_id"] > 0
    assert body["sale_id"] == sale["sale_id"]
    assert body["product_id"] == product["product_id"]
    assert body["quantity"] == 3
    assert money(body["unit_price"]) == Decimal("10.00")
    assert money(body["discount_amount"]) == Decimal("5.00")
    assert money(body["subtotal"]) == Decimal("25.00")


def test_subtotal_is_calculated_when_it_is_zero(client, make_sale, make_product):
    sale = make_sale()
    product = make_product()

    response = client.post(
        SALE_ITEMS,
        json=item_payload(sale["sale_id"], product["product_id"], subtotal="0"),
    )

    assert response.status_code == 201
    assert money(response.json()["subtotal"]) == Decimal("25.00")


def test_explicit_subtotal_is_kept(client, make_sale, make_product):
    sale = make_sale()
    product = make_product()

    response = client.post(
        SALE_ITEMS,
        json=item_payload(sale["sale_id"], product["product_id"], subtotal="99.00"),
    )

    assert response.status_code == 201
    assert money(response.json()["subtotal"]) == Decimal("99.00")


def test_list_sale_items(client, make_sale_item):
    made = [make_sale_item(), make_sale_item()]

    response = client.get(SALE_ITEMS)

    assert response.status_code == 200
    assert {i["sale_item_id"] for i in response.json()} == {
        i["sale_item_id"] for i in made
    }


def test_get_sale_item_by_id(client, make_sale_item):
    item = make_sale_item(quantity=7)

    response = client.get(f"{SALE_ITEMS}{item['sale_item_id']}")

    assert response.status_code == 200
    assert response.json()["quantity"] == 7


def test_update_recalculates_the_subtotal(client, make_sale_item):
    item = make_sale_item(
        quantity=2, unit_price="10.00", discount_amount="5.00", subtotal="15.00"
    )

    response = client.put(f"{SALE_ITEMS}{item['sale_item_id']}", json={"quantity": 4})

    assert response.status_code == 200
    body = response.json()
    assert body["quantity"] == 4
    assert money(body["subtotal"]) == Decimal("35.00")


def test_updating_the_unit_price_recalculates_the_subtotal(client, make_sale_item):
    item = make_sale_item(
        quantity=2, unit_price="10.00", discount_amount="0.00", subtotal="20.00"
    )

    response = client.put(
        f"{SALE_ITEMS}{item['sale_item_id']}", json={"unit_price": "12.50"}
    )

    assert response.status_code == 200
    assert money(response.json()["subtotal"]) == Decimal("25.00")


def test_delete_sale_item(client, make_sale_item):
    item = make_sale_item()
    url = f"{SALE_ITEMS}{item['sale_item_id']}"

    response = client.delete(url)

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(url).status_code == 404


@pytest.mark.parametrize(
    "missing",
    ["sale_id", "product_id", "quantity", "unit_price", "discount_amount", "subtotal"],
)
def test_create_sale_item_missing_required_field_returns_422(
    client, make_sale, make_product, missing
):
    payload = item_payload(make_sale()["sale_id"], make_product()["product_id"])
    del payload[missing]

    response = client.post(SALE_ITEMS, json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field, bad_value",
    [
        ("quantity", "many"),
        ("quantity", 2.5),
        ("unit_price", "cheap"),
        ("discount_amount", "some"),
        ("sale_id", "abc"),
    ],
)
def test_create_sale_item_with_invalid_value_returns_422(
    client, make_sale, make_product, field, bad_value
):
    payload = item_payload(make_sale()["sale_id"], make_product()["product_id"])
    payload[field] = bad_value

    response = client.post(SALE_ITEMS, json=payload)

    assert response.status_code == 422


def test_create_sale_item_for_unknown_sale_returns_409(client, make_product):
    response = client.post(
        SALE_ITEMS, json=item_payload(99999, make_product()["product_id"])
    )

    assert response.status_code == 409


def test_create_sale_item_for_unknown_product_returns_409(client, make_sale):
    response = client.post(SALE_ITEMS, json=item_payload(make_sale()["sale_id"], 99999))

    assert response.status_code == 409


def test_update_sale_item_to_unknown_product_returns_409(client, make_sale_item):
    item = make_sale_item()

    response = client.put(
        f"{SALE_ITEMS}{item['sale_item_id']}", json={"product_id": 99999}
    )

    assert response.status_code == 409