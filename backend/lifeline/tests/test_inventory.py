import uuid
from .conftest import make_product


class TestInventoryAdjustments:
    def test_restock_increases_stock_and_logs_it(self, client, admin_headers):
        product = make_product(client, admin_headers, current_stock=10)
        resp = client.post(
            "/api/v1/inventory/adjust",
            json={"product_id": product["product_id"], "quantity_changed": 20, "reason": "restock"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["previous_quantity"] == 10
        assert body["new_quantity"] == 30

        updated = client.get(f"/api/v1/products/{product['product_id']}", headers=admin_headers).json()
        assert updated["current_stock"] == 30

    def test_write_off_decreases_stock(self, client, admin_headers):
        product = make_product(client, admin_headers, current_stock=10)
        resp = client.post(
            "/api/v1/inventory/adjust",
            json={"product_id": product["product_id"], "quantity_changed": -3, "reason": "damage", "note": "dropped box"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["new_quantity"] == 7

    def test_adjustment_below_zero_is_blocked_by_default(self, client, admin_headers):
        product = make_product(client, admin_headers, current_stock=5)
        resp = client.post(
            "/api/v1/inventory/adjust",
            json={"product_id": product["product_id"], "quantity_changed": -10, "reason": "damage"},
            headers=admin_headers,
        )
        assert resp.status_code == 409
        unchanged = client.get(f"/api/v1/products/{product['product_id']}", headers=admin_headers).json()
        assert unchanged["current_stock"] == 5

    def test_adjustment_below_zero_succeeds_with_override(self, client, admin_headers):
        product = make_product(client, admin_headers, current_stock=5)
        resp = client.post(
            "/api/v1/inventory/adjust",
            json={
                "product_id": product["product_id"], "quantity_changed": -10,
                "reason": "correction", "allow_negative_stock": True,
            },
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["new_quantity"] == -5

    def test_zero_quantity_adjustment_is_a_no_op_but_still_logged(self, client, admin_headers):
        product = make_product(client, admin_headers, current_stock=10)
        resp = client.post(
            "/api/v1/inventory/adjust",
            json={"product_id": product["product_id"], "quantity_changed": 0, "reason": "correction"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["new_quantity"] == 10

    def test_adjustment_on_nonexistent_product_returns_404(self, client, admin_headers):
        resp = client.post(
            "/api/v1/inventory/adjust",
            json={"product_id": str(uuid.uuid4()), "quantity_changed": 5, "reason": "restock"},
            headers=admin_headers,
        )
        assert resp.status_code == 404

    def test_invalid_reason_enum_value_is_rejected(self, client, admin_headers):
        product = make_product(client, admin_headers)
        resp = client.post(
            "/api/v1/inventory/adjust",
            json={"product_id": product["product_id"], "quantity_changed": 5, "reason": "made_up_reason"},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_logs_are_retrievable_and_filterable_by_product(self, client, admin_headers):
        product_a = make_product(client, admin_headers)
        product_b = make_product(client, admin_headers)
        client.post("/api/v1/inventory/adjust", json={"product_id": product_a["product_id"], "quantity_changed": 5, "reason": "restock"}, headers=admin_headers)
        client.post("/api/v1/inventory/adjust", json={"product_id": product_b["product_id"], "quantity_changed": 5, "reason": "restock"}, headers=admin_headers)

        resp = client.get(f"/api/v1/inventory/logs?product_id={product_a['product_id']}", headers=admin_headers)
        assert resp.status_code == 200
        assert all(log["product_id"] == product_a["product_id"] for log in resp.json())
        assert len(resp.json()) >= 1
