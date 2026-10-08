import uuid

from .conftest import make_product


class TestSyncPush:
    def test_create_sale_operation_applies_once(self, client, admin_headers):
        product = make_product(
            client, admin_headers, selling_price=100, current_stock=10
        )
        idem_key = str(uuid.uuid4())
        operation = {
            "device_id": "test-device-1",
            "idempotency_key": idem_key,
            "operation_type": "create_sale",
            "payload": {
                "idempotency_key": idem_key,
                "items": [{"product_id": product["product_id"], "quantity": 1}],
                "payments": [{"method": "cash", "amount": 100}],
            },
        }
        resp = client.post(
            "/api/v1/sync/push", json={"operations": [operation]}, headers=admin_headers
        )
        assert resp.status_code == 200
        assert resp.json()["results"][0]["status"] == "applied"

    def test_replaying_the_same_operation_is_reported_as_already_applied(
        self, client, admin_headers
    ):
        product = make_product(
            client, admin_headers, selling_price=100, current_stock=10
        )
        idem_key = str(uuid.uuid4())
        operation = {
            "device_id": "test-device-1",
            "idempotency_key": idem_key,
            "operation_type": "create_sale",
            "payload": {
                "idempotency_key": idem_key,
                "items": [{"product_id": product["product_id"], "quantity": 1}],
                "payments": [{"method": "cash", "amount": 100}],
            },
        }
        first = client.post(
            "/api/v1/sync/push", json={"operations": [operation]}, headers=admin_headers
        )
        assert first.json()["results"][0]["status"] == "applied"

        second = client.post(
            "/api/v1/sync/push", json={"operations": [operation]}, headers=admin_headers
        )
        assert second.json()["results"][0]["status"] == "already_applied"

        updated = client.get(
            f"/api/v1/products/{product['product_id']}", headers=admin_headers
        ).json()
        assert updated["current_stock"] == 9

    def test_unknown_operation_type_fails_gracefully(self, client, admin_headers):
        operation = {
            "device_id": "test-device-1",
            "idempotency_key": str(uuid.uuid4()),
            "operation_type": "launch_missiles",
            "payload": {},
        }
        resp = client.post(
            "/api/v1/sync/push", json={"operations": [operation]}, headers=admin_headers
        )
        assert resp.status_code == 200
        assert resp.json()["results"][0]["status"] == "failed"

    def test_one_bad_operation_does_not_block_others_in_the_same_batch(
        self, client, admin_headers
    ):
        product = make_product(
            client, admin_headers, selling_price=100, current_stock=10
        )
        good_key = str(uuid.uuid4())
        good_op = {
            "device_id": "d1",
            "idempotency_key": good_key,
            "operation_type": "create_sale",
            "payload": {
                "idempotency_key": good_key,
                "items": [{"product_id": product["product_id"], "quantity": 1}],
                "payments": [{"method": "cash", "amount": 100}],
            },
        }
        bad_op = {
            "device_id": "d1",
            "idempotency_key": str(uuid.uuid4()),
            "operation_type": "nonsense",
            "payload": {},
        }

        resp = client.post(
            "/api/v1/sync/push",
            json={"operations": [bad_op, good_op]},
            headers=admin_headers,
        )
        statuses = {r["idempotency_key"]: r["status"] for r in resp.json()["results"]}
        assert statuses[good_key] == "applied"
        assert statuses[bad_op["idempotency_key"]] == "failed"

    def test_adjust_inventory_operation_applies(self, client, admin_headers):
        product = make_product(client, admin_headers, current_stock=10)
        operation = {
            "device_id": "d1",
            "idempotency_key": str(uuid.uuid4()),
            "operation_type": "adjust_inventory",
            "payload": {
                "product_id": product["product_id"],
                "quantity_changed": 5,
                "reason": "restock",
            },
        }
        resp = client.post(
            "/api/v1/sync/push", json={"operations": [operation]}, headers=admin_headers
        )
        assert resp.json()["results"][0]["status"] == "applied"
        updated = client.get(
            f"/api/v1/products/{product['product_id']}", headers=admin_headers
        ).json()
        assert updated["current_stock"] == 15

    def test_empty_operations_list_returns_empty_results(self, client, admin_headers):
        resp = client.post(
            "/api/v1/sync/push", json={"operations": []}, headers=admin_headers
        )
        assert resp.status_code == 200
        assert resp.json()["results"] == []


class TestSyncPull:
    def test_pull_returns_active_products_and_settings(self, client, admin_headers):
        make_product(client, admin_headers)
        resp = client.get("/api/v1/sync/pull", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "products_updated_since" in body
        assert "settings" in body
        assert len(body["products_updated_since"]) >= 1
