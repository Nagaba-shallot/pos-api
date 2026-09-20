import pytest

SUPPLIERS = "/suppliers/"

VALID_SUPPLIER = {
    "company_name": "Acme Supplies",
    "contact_person": "John Doe",
    "contact_email": "john@acme.example.com",
    "contact_phone": "0700123456",
    "address": "1 Industrial Road",
}


def test_create_supplier(client):
    response = client.post(SUPPLIERS, json=VALID_SUPPLIER)

    assert response.status_code == 201
    body = response.json()
    assert body["supplier_id"] > 0
    for field, value in VALID_SUPPLIER.items():
        assert body[field] == value
    assert body["created_at"]


def test_list_suppliers(client, make_supplier):
    made = [make_supplier(), make_supplier(), make_supplier()]

    response = client.get(SUPPLIERS)

    assert response.status_code == 200
    assert {s["supplier_id"] for s in response.json()} == {s["supplier_id"] for s in made}


def test_get_supplier_by_id(client, make_supplier):
    supplier = make_supplier(company_name="Fresh Farms")

    response = client.get(f"{SUPPLIERS}{supplier['supplier_id']}")

    assert response.status_code == 200
    assert response.json()["company_name"] == "Fresh Farms"


def test_update_supplier(client, make_supplier):
    supplier = make_supplier()

    response = client.put(
        f"{SUPPLIERS}{supplier['supplier_id']}",
        json={"company_name": "Renamed Ltd", "address": "New Address"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["company_name"] == "Renamed Ltd"
    assert body["address"] == "New Address"
    assert body["contact_email"] == supplier["contact_email"]


def test_delete_supplier(client, make_supplier):
    supplier = make_supplier()
    url = f"{SUPPLIERS}{supplier['supplier_id']}"

    response = client.delete(url)

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(url).status_code == 404


@pytest.mark.parametrize("missing", list(VALID_SUPPLIER))
def test_create_supplier_missing_required_field_returns_422(client, missing):
    payload = {k: v for k, v in VALID_SUPPLIER.items() if k != missing}

    response = client.post(SUPPLIERS, json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field, value",
    [
        ("company_name", "Acme Supplies"),
        ("contact_person", "John Doe"),
        ("contact_email", "john@acme.example.com"),
        ("contact_phone", "0700123456"),
    ],
)
def test_duplicate_unique_field_returns_409(client, make_supplier, field, value):
    make_supplier(**{field: value})
    other = {
        "company_name": "Another Company",
        "contact_person": "Someone Else",
        "contact_email": "other@example.com",
        "contact_phone": "0799999999",
        "address": "Elsewhere",
        field: value,
    }

    response = client.post(SUPPLIERS, json=other)

    assert response.status_code == 409


def test_update_to_an_existing_company_name_returns_409(client, make_supplier):
    first = make_supplier()
    second = make_supplier()

    response = client.put(
        f"{SUPPLIERS}{second['supplier_id']}",
        json={"company_name": first["company_name"]},
    )

    assert response.status_code == 409


def test_deleting_a_supplier_keeps_its_products(
    client, auth_headers, make_supplier, make_product
):
    supplier = make_supplier()
    product = make_product(supplier_id=supplier["supplier_id"])

    response = client.delete(f"{SUPPLIERS}{supplier['supplier_id']}")

    assert response.status_code == 204
    remaining = client.get(f"/products/{product['product_id']}", headers=auth_headers)
    assert remaining.status_code == 200
    assert remaining.json()["supplier_id"] is None