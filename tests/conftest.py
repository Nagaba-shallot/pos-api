import os

os.environ["DATABASE_URL"] = "sqlite://"

import itertools  

import pytest  
from fastapi.testclient import TestClient  

from database import Base, engine  
from main import app  

assert engine.dialect.name == "sqlite", (
    f"Tests must run against SQLite, not {engine.dialect.name!r}"
)

SALE_DATE = "2026-09-20T10:00:00"
_counter = itertools.count(1)


def _unique() -> int:
    return next(_counter)


def _create(client, path, payload, headers=None):
    response = client.post(path, json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()

@pytest.fixture(autouse=True)
def _fresh_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_user_data():
    return {
        "username": "cashier1",
        "password": "Passw0rd!123",
        "email": "cashier1@example.com",
        "role": "admin",
        "first_name": "Nasha",
        "last_name": "Pretty",
    }


@pytest.fixture
def auth_headers(client, auth_user_data):
    register = client.post("/auth/register", json=auth_user_data)
    assert register.status_code == 201, register.text
    login = client.post(
        "/auth/login",
        data={
            "username": auth_user_data["username"],
            "password": auth_user_data["password"],
        },
    )
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.fixture
def make_user(client):
    def _make(**overrides):
        n = _unique()
        payload = {
            "username": f"user{n}",
            "password": "S3cret-pass!",
            "email": f"user{n}@example.com",
            "role": "cashier",
            "first_name": "Test",
            "last_name": f"User{n}",
        }
        payload.update(overrides)
        return _create(client, "/users/", payload)

    return _make


@pytest.fixture
def make_category(client):
    def _make(**overrides):
        n = _unique()
        payload = {
            "name": f"Category {n}",
            "category_description": f"Description {n}",
        }
        payload.update(overrides)
        return _create(client, "/categories/", payload)

    return _make


@pytest.fixture
def make_supplier(client):
    def _make(**overrides):
        n = _unique()
        payload = {
            "company_name": f"Supplier {n} Ltd",
            "contact_person": f"Contact {n}",
            "contact_email": f"supplier{n}@example.com",
            "contact_phone": f"0700{n:06d}",
            "address": f"{n} Market Street",
        }
        payload.update(overrides)
        return _create(client, "/suppliers/", payload)

    return _make


@pytest.fixture
def make_customer(client):
    def _make(**overrides):
        n = _unique()
        payload = {
            "first_name": "Nasha",
            "last_name": f"Customer{n}",
            "email": f"customer{n}@example.com",
            "phone_number": f"0711{n:06d}",
            "address": f"{n} High Street",
        }
        payload.update(overrides)
        return _create(client, "/customers/", payload)

    return _make


@pytest.fixture
def make_product(client, auth_headers, make_category):
    def _make(**overrides):
        n = _unique()
        payload = {
            "name": f"Product {n}",
            "stock_keeping_unit": f"SKU-{n:05d}",
            "price": "9.99",
            "quantity_in_stock": 100,
            "reorder_level": 10,
        }
        payload.update(overrides)
        if "category_id" not in payload:
            payload["category_id"] = make_category()["category_id"]
        return _create(client, "/products/", payload, headers=auth_headers)

    return _make


@pytest.fixture
def make_sale(client, make_customer, make_user):
    def _make(**overrides):
        payload = {
            "sale_date": SALE_DATE,
            "total_amount": "100.00",
            "tax_amount": "16.00",
            "discount_amount": "0.00",
        }
        payload.update(overrides)
        if "customer_id" not in payload:
            payload["customer_id"] = make_customer()["customer_id"]
        if "user_id" not in payload:
            payload["user_id"] = make_user()["id"]
        return _create(client, "/sales/", payload)

    return _make


@pytest.fixture
def make_sale_item(client, make_sale, make_product):
    def _make(**overrides):
        payload = {
            "quantity": 2,
            "unit_price": "10.00",
            "discount_amount": "0.00",
            "subtotal": "20.00",
        }
        payload.update(overrides)
        if "sale_id" not in payload:
            payload["sale_id"] = make_sale()["sale_id"]
        if "product_id" not in payload:
            payload["product_id"] = make_product()["product_id"]
        return _create(client, "/sale-items/", payload)

    return _make


@pytest.fixture
def make_payment(client, make_sale):
    def _make(**overrides):
        payload = {
            "payment_method": "cash",
            "payment_amount": "100.00",
            "payment_date": SALE_DATE,
        }
        payload.update(overrides)
        if "sale_id" not in payload:
            payload["sale_id"] = make_sale()["sale_id"]
        return _create(client, "/payments/", payload)

    return _make


@pytest.fixture
def make_receipt(client, make_sale):
    def _make(**overrides):
        payload = {
            "printed_time": SALE_DATE,
            "receipt_text": "Thank you for shopping with us!",
        }
        payload.update(overrides)
        if "sale_id" not in payload:
            payload["sale_id"] = make_sale()["sale_id"]
        return _create(client, "/receipts/", payload)

    return _make