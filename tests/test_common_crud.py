import pytest

MISSING_ID = 99999

RESOURCES = [
    pytest.param("/categories/", False, id="categories"),
    pytest.param("/customers/", False, id="customers"),
    pytest.param("/payments/", False, id="payments"),
    pytest.param("/products/", True, id="products"),
    pytest.param("/receipts/", False, id="receipts"),
    pytest.param("/sale-items/", False, id="sale-items"),
    pytest.param("/sales/", False, id="sales"),
    pytest.param("/suppliers/", False, id="suppliers"),
    pytest.param("/users/", False, id="users"),
]


@pytest.fixture
def headers(request):
    needs_auth = request.node.callspec.params["needs_auth"]
    return request.getfixturevalue("auth_headers") if needs_auth else {}


@pytest.mark.parametrize("path, needs_auth", RESOURCES)
def test_list_is_empty_on_a_fresh_database(client, headers, path, needs_auth):
    response = client.get(path, headers=headers)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("path, needs_auth", RESOURCES)
def test_get_missing_record_returns_404(client, headers, path, needs_auth):
    response = client.get(f"{path}{MISSING_ID}", headers=headers)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.parametrize("path, needs_auth", RESOURCES)
def test_update_missing_record_returns_404(client, headers, path, needs_auth):
    response = client.put(f"{path}{MISSING_ID}", json={}, headers=headers)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.parametrize("path, needs_auth", RESOURCES)
def test_delete_missing_record_returns_404(client, headers, path, needs_auth):
    response = client.delete(f"{path}{MISSING_ID}", headers=headers)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.parametrize("path, needs_auth", RESOURCES)
def test_non_integer_id_returns_422(client, headers, path, needs_auth):
    response = client.get(f"{path}abc", headers=headers)

    assert response.status_code == 422


@pytest.mark.parametrize("path, needs_auth", RESOURCES)
def test_create_with_empty_body_returns_422(client, headers, path, needs_auth):
    response = client.post(path, json={}, headers=headers)

    assert response.status_code == 422


@pytest.mark.parametrize("path, needs_auth", RESOURCES)
def test_create_with_malformed_json_returns_422(client, headers, path, needs_auth):
    response = client.post(
        path,
        content="{this is not json",
        headers={**headers, "Content-Type": "application/json"},
    )

    assert response.status_code == 422


@pytest.mark.parametrize("path, needs_auth", RESOURCES)
def test_unsupported_method_returns_405(client, headers, path, needs_auth):
    response = client.patch(f"{path}1", json={}, headers=headers)

    assert response.status_code == 405