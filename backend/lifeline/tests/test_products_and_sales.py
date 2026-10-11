def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_product_minimal(client, admin_token):
    resp = client.post(
        "/api/v1/products/",
        json={"product_name": "Test Soda", "selling_price": 50, "current_stock": 10},
        headers=_auth_headers(admin_token),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["product_name"] == "Test Soda"
    assert body["current_stock"] == 10
    assert body["stock_status"] == "healthy"


def test_sale_reduces_stock_and_is_idempotent(client, admin_token):
    headers = _auth_headers(admin_token)
    product = client.post(
        "/api/v1/products/",
        json={"product_name": "Test Bread", "selling_price": 65, "current_stock": 5},
        headers=headers,
    ).json()

    sale_payload = {
        "idempotency_key": "test-key-001",
        "items": [{"product_id": product["product_id"], "quantity": 2}],
        "payments": [{"method": "cash", "amount": 130, "amount_tendered": 130}],
    }
    resp1 = client.post("/api/v1/sales/", json=sale_payload, headers=headers)
    assert resp1.status_code == 201, resp1.text
    sale1 = resp1.json()
    assert float(sale1["total_amount"]) == 130

    resp2 = client.post("/api/v1/sales/", json=sale_payload, headers=headers)
    assert resp2.status_code == 201
    assert resp2.json()["sale_id"] == sale1["sale_id"]

    updated_product = client.get(f"/api/v1/products/{product['product_id']}", headers=headers).json()
    assert updated_product["current_stock"] == 3


def test_sale_blocks_insufficient_stock_by_default(client, admin_token):
    headers = _auth_headers(admin_token)
    product = client.post(
        "/api/v1/products/",
        json={"product_name": "Scarce Item", "selling_price": 100, "current_stock": 1},
        headers=headers,
    ).json()

    resp = client.post(
        "/api/v1/sales/",
        json={
            "idempotency_key": "test-key-002",
            "items": [{"product_id": product["product_id"], "quantity": 5}],
            "payments": [{"method": "cash", "amount": 500}],
        },
        headers=headers,
    )
    assert resp.status_code == 409


def test_cashier_cannot_view_profit(client, admin_token):
    headers = _auth_headers(admin_token)
    cashier_resp = client.post(
        "/api/v1/users/",
        json={"email": "cashier@test.com", "password": "password123", "first_name": "Cash", "last_name": "Ier", "role": "Cashier"},
        headers=headers,
    )
    assert cashier_resp.status_code == 201

    login = client.post("/api/v1/auth/login", data={"username": "cashier@test.com", "password": "password123"})
    cashier_headers = _auth_headers(login.json()["access_token"])

    resp = client.get("/api/v1/reports/profit-summary", headers=cashier_headers)
    assert resp.status_code == 403
