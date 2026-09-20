CATEGORIES = "/categories/"


def test_create_category(client):
    response = client.post(
        CATEGORIES, json={"name": "Beverages", "category_description": "Drinks"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["category_id"] > 0
    assert body["name"] == "Beverages"
    assert body["category_description"] == "Drinks"
    assert body["created_at"]
    assert body["updated_at"]


def test_create_category_without_description(client):
    response = client.post(CATEGORIES, json={"name": "Snacks"})

    assert response.status_code == 201
    assert response.json()["category_description"] is None


def test_list_categories(client, make_category):
    first = make_category()
    second = make_category()

    response = client.get(CATEGORIES)

    assert response.status_code == 200
    ids = {c["category_id"] for c in response.json()}
    assert ids == {first["category_id"], second["category_id"]}


def test_get_category_by_id(client, make_category):
    category = make_category(name="Bakery")

    response = client.get(f"{CATEGORIES}{category['category_id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Bakery"


def test_update_category(client, make_category):
    category = make_category(name="Old", category_description="Old description")

    response = client.put(
        f"{CATEGORIES}{category['category_id']}",
        json={"name": "New", "category_description": "New description"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "New"
    assert body["category_description"] == "New description"


def test_partial_update_keeps_other_fields(client, make_category):
    category = make_category(name="Keep me", category_description="Before")

    response = client.put(
        f"{CATEGORIES}{category['category_id']}",
        json={"category_description": "After"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Keep me"
    assert response.json()["category_description"] == "After"


def test_delete_category(client, make_category):
    category = make_category()
    url = f"{CATEGORIES}{category['category_id']}"

    response = client.delete(url)

    assert response.status_code == 200
    assert response.json()["category_id"] == category["category_id"]
    assert client.get(url).status_code == 404


def test_create_category_without_name_returns_422(client):
    response = client.post(CATEGORIES, json={"category_description": "No name"})

    assert response.status_code == 422


def test_create_category_with_null_name_returns_422(client):
    response = client.post(CATEGORIES, json={"name": None})

    assert response.status_code == 422


def test_create_category_with_wrong_type_returns_422(client):
    response = client.post(CATEGORIES, json={"name": ["not", "a", "string"]})

    assert response.status_code == 422


def test_cannot_delete_category_that_still_has_products(
    client, auth_headers, make_category, make_product
):
    category = make_category()
    product = make_product(category_id=category["category_id"])

    response = client.delete(f"{CATEGORIES}{category['category_id']}")

    assert response.status_code == 409
    assert client.get(f"{CATEGORIES}{category['category_id']}").status_code == 200
    assert (
        client.get(f"/products/{product['product_id']}", headers=auth_headers).status_code
        == 200
    )