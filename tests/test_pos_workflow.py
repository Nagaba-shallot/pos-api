from decimal import Decimal


def money(value):
    return Decimal(str(value))


def test_complete_sale_workflow(
    client, auth_headers, make_user, make_customer, make_category, make_supplier
):
    cashier = make_user(role="cashier")
    customer = make_customer()
    category = make_category(name="Groceries")
    supplier = make_supplier()

    # Stock a product 
    product_response = client.post(
        "/products/",
        json={
            "name": "Rice 2kg",
            "stock_keeping_unit": "RICE-2KG",
            "price": "10.00",
            "quantity_in_stock": 50,
            "reorder_level": 5,
            "category_id": category["category_id"],
            "supplier_id": supplier["supplier_id"],
        },
        headers=auth_headers,
    )
    assert product_response.status_code == 201
    product = product_response.json()

    # Ring up a sale for that customer, served by that cashier.
    sale_response = client.post(
        "/sales/",
        json={
            "customer_id": customer["customer_id"],
            "user_id": cashier["id"],
            "sale_date": "2026-09-20T09:30:00",
            "total_amount": "25.00",
            "tax_amount": "0.00",
            "discount_amount": "5.00",
        },
    )
    assert sale_response.status_code == 201
    sale = sale_response.json()

    # Add a line item; the subtotal is worked out when it is sent as 0.
    item_response = client.post(
        "/sale-items/",
        json={
            "sale_id": sale["sale_id"],
            "product_id": product["product_id"],
            "quantity": 3,
            "unit_price": "10.00",
            "discount_amount": "5.00",
            "subtotal": "0",
        },
    )
    assert item_response.status_code == 201
    item = item_response.json()
    assert money(item["subtotal"]) == Decimal("25.00")

    # Take payment and issue a receipt.
    payment_response = client.post(
        "/payments/",
        json={
            "sale_id": sale["sale_id"],
            "payment_method": "cash",
            "payment_amount": "25.00",
            "payment_date": "2026-09-20T09:31:00",
        },
    )
    assert payment_response.status_code == 201
    payment = payment_response.json()

    receipt_response = client.post(
        "/receipts/",
        json={
            "sale_id": sale["sale_id"],
            "receipt_text": "Rice 2kg x3 - 25.00",
            "printed_time": "2026-09-20T09:31:30",
        },
    )
    assert receipt_response.status_code == 201
    receipt = receipt_response.json()

    # Everything can be read back and is linked to the same sale.
    assert client.get(f"/sales/{sale['sale_id']}").json()["customer_id"] == customer["customer_id"]
    assert client.get(f"/sale-items/{item['sale_item_id']}").json()["sale_id"] == sale["sale_id"]
    assert client.get(f"/payments/{payment['payment_id']}").json()["sale_id"] == sale["sale_id"]
    assert client.get(f"/receipts/{receipt['receipt_id']}").json()["sale_id"] == sale["sale_id"]

    # The sale (and the product that was sold) are protected while in use...
    assert client.delete(f"/sales/{sale['sale_id']}").status_code == 409
    assert (
        client.delete(f"/products/{product['product_id']}", headers=auth_headers).status_code
        == 409
    )

    # ...and can be removed once the records that depend on them are gone.
    assert client.delete(f"/receipts/{receipt['receipt_id']}").status_code == 204
    assert client.delete(f"/payments/{payment['payment_id']}").status_code == 204
    assert client.delete(f"/sale-items/{item['sale_item_id']}").status_code == 204
    assert client.delete(f"/sales/{sale['sale_id']}").status_code == 204
    assert (
        client.delete(f"/products/{product['product_id']}", headers=auth_headers).status_code
        == 204
    )