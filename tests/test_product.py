from decimal import Decimal

import pytest

PRODUCTS = "/products/"


def money(value):
    return Decimal(str(value))


def product_payload(category_id, **overrides):
    payload = {
        "name": "Widget",
        "stock_keeping_unit": "SKU-WIDGET-1",
        "price": "9.99",
        "quantity_in_stock": 100,
        "reorder_level": 10,
        "category_id": category_id,
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize(
    "method, path",
    [
        ("GET", "/products/"),
        ("GET", "/products/1"),
        ("POST", "/products/"),
        ("PUT", "/products/1"),
        ("DELETE", "/products/1"),
    ],
)
def test_every_product_endpoint_requires_a_token(client, method, path):
    kwargs = {"json": {}} if method in ("POST", "PUT") else {}

    response = client.request(method, path, **kwargs)

    assert response.status_code == 401


def test_invalid_token_is_rejected(client):
    response = client.get(PRODUCTS, headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401


def test_create_product(client, auth_headers, make_category, make_supplier):
    category = make_category()
    supplier = make_supplier()

    response = client.post(
        PRODUCTS,
        json=product_payload(category["category_id"], supplier_id=supplier["supplier_id"]),
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["product_id"] > 0
    assert body["name"] == "Widget"
    assert body["stock_keeping_unit"] == "SKU-WIDGET-1"
    assert money(body["price"]) == Decimal("9.99")
    assert body["quantity_in_stock"] == 100
    assert body["reorder_level"] == 10
    assert body["category_id"] == category["category_id"]
    assert body["supplier_id"] == supplier["supplier_id"]
    assert body["created_at"]


def test_create_product_without_supplier(client, auth_headers, make_category):
    category = make_category()

    response = client.post(
        PRODUCTS, json=product_payload(category["category_id"]), headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["supplier_id"] is None


def test_list_products(client, auth_headers, make_product):
    made = [make_product(), make_product(), make_product()]

    response = client.get(PRODUCTS, headers=auth_headers)

    assert response.status_code == 200
    assert {p["product_id"] for p in response.json()} == {p["product_id"] for p in made}


def test_get_product_by_id(client, auth_headers, make_product):
    product = make_product(name="Coffee Beans")

    response = client.get(f"{PRODUCTS}{product['product_id']}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Coffee Beans"


def test_update_product(client, auth_headers, make_product):
    product = make_product(price="5.00", quantity_in_stock=10)

    response = client.put(
        f"{PRODUCTS}{product['product_id']}",
        json={"name": "Renamed", "price": "7.50", "quantity_in_stock": 25},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Renamed"
    assert money(body["price"]) == Decimal("7.50")
    assert body["quantity_in_stock"] == 25
    assert body["stock_keeping_unit"] == product["stock_keeping_unit"]
    assert body["reorder_level"] == product["reorder_level"]
    assert body["category_id"] == product["category_id"]


def test_updates_are_persisted(client, auth_headers, make_product):
    product = make_product(quantity_in_stock=10)
    url = f"{PRODUCTS}{product['product_id']}"

    client.put(url, json={"quantity_in_stock": 3}, headers=auth_headers)

    assert client.get(url, headers=auth_headers).json()["quantity_in_stock"] == 3


def test_delete_product(client, auth_headers, make_product):
    product = make_product()
    url = f"{PRODUCTS}{product['product_id']}"

    response = client.delete(url, headers=auth_headers)

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(url, headers=auth_headers).status_code == 404


@pytest.mark.parametrize(
    "missing",
    ["name", "stock_keeping_unit", "price", "quantity_in_stock", "reorder_level", "category_id"],
)
def test_create_product_missing_required_field_returns_422(
    client, auth_headers, make_category, missing
):
    payload = product_payload(make_category()["category_id"])
    del payload[missing]

    response = client.post(PRODUCTS, json=payload, headers=auth_headers)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field, bad_value",
    [
        ("price", "not-a-number"),
        ("quantity_in_stock", "lots"),
        ("quantity_in_stock", 1.5),
        ("reorder_level", "soon"),
        ("category_id", "abc"),
        ("name", None),
    ],
)
def test_create_product_with_invalid_value_returns_422(
    client, auth_headers, make_category, field, bad_value
):
    payload = product_payload(make_category()["category_id"])
    payload[field] = bad_value

    response = client.post(PRODUCTS, json=payload, headers=auth_headers)

    assert response.status_code == 422


def test_update_product_with_invalid_value_returns_422(client, auth_headers, make_product):
    product = make_product()

    response = client.put(
        f"{PRODUCTS}{product['product_id']}",
        json={"price": "free"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_duplicate_sku_returns_409(client, auth_headers, make_product, make_category):
    existing = make_product()

    response = client.post(
        PRODUCTS,
        json=product_payload(
            make_category()["category_id"],
            stock_keeping_unit=existing["stock_keeping_unit"],
        ),
        headers=auth_headers,
    )

    assert response.status_code == 409


def test_update_to_an_existing_sku_returns_409(client, auth_headers, make_product):
    first = make_product()
    second = make_product()

    response = client.put(
        f"{PRODUCTS}{second['product_id']}",
        json={"stock_keeping_unit": first["stock_keeping_unit"]},
        headers=auth_headers,
    )

    assert response.status_code == 409


def test_create_product_with_unknown_category_returns_409(client, auth_headers):
    response = client.post(
        PRODUCTS, json=product_payload(category_id=99999), headers=auth_headers
    )

    assert response.status_code == 409


def test_create_product_with_unknown_supplier_returns_409(
    client, auth_headers, make_category
):
    response = client.post(
        PRODUCTS,
        json=product_payload(make_category()["category_id"], supplier_id=99999),
        headers=auth_headers,
    )

    assert response.status_code == 409


def test_update_product_to_unknown_category_returns_409(client, auth_headers, make_product):
    product = make_product()

    response = client.put(
        f"{PRODUCTS}{product['product_id']}",
        json={"category_id": 99999},
        headers=auth_headers,
    )

    assert response.status_code == 409


def test_cannot_delete_product_that_has_been_sold(client, auth_headers, make_product, make_sale_item):
    product = make_product()
    make_sale_item(product_id=product["product_id"])

    response = client.delete(f"{PRODUCTS}{product['product_id']}", headers=auth_headers)

    assert response.status_code == 409
    assert (
        client.get(f"{PRODUCTS}{product['product_id']}", headers=auth_headers).status_code
        == 200
    )