def test_root_returns_welcome_message(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Point of Sale API"}


def test_unknown_route_returns_404(client):
    response = client.get("/does-not-exist")

    assert response.status_code == 404


def test_interactive_docs_are_served(client):
    assert client.get("/docs").status_code == 200


def test_openapi_schema_exposes_every_resource(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    for prefix in (
        "/auth/login",
        "/auth/register",
        "/categories/",
        "/customers/",
        "/payments/",
        "/products/",
        "/receipts/",
        "/sale-items/",
        "/sales/",
        "/suppliers/",
        "/users/",
    ):
        assert prefix in paths, f"{prefix} missing from the OpenAPI schema"