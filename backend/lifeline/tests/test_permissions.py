from .conftest import make_product


class TestRolePermissions:
    def test_cashier_cannot_create_products(self, client, cashier_headers):
        resp = client.post(
            "/api/v1/products/",
            json={"product_name": "X", "selling_price": 10, "current_stock": 1},
            headers=cashier_headers,
        )
        assert resp.status_code == 403

    def test_manager_can_create_products(self, client, manager_headers):
        resp = client.post(
            "/api/v1/products/",
            json={"product_name": "Y", "selling_price": 10, "current_stock": 1},
            headers=manager_headers,
        )
        assert resp.status_code == 201

    def test_cashier_cannot_view_profit_report(self, client, cashier_headers):
        resp = client.get("/api/v1/reports/profit-summary", headers=cashier_headers)
        assert resp.status_code == 403

    def test_manager_can_view_profit_report(self, client, manager_headers):
        resp = client.get("/api/v1/reports/profit-summary", headers=manager_headers)
        assert resp.status_code == 200

    def test_cashier_cannot_manage_users(self, client, cashier_headers):
        resp = client.get("/api/v1/users/", headers=cashier_headers)
        assert resp.status_code == 403

    def test_only_admin_and_manager_can_adjust_inventory(
        self, client, admin_headers, manager_headers, cashier_headers
    ):
        product = make_product(client, admin_headers)
        payload = {
            "product_id": product["product_id"],
            "quantity_changed": 5,
            "reason": "restock",
        }

        assert (
            client.post(
                "/api/v1/inventory/adjust", json=payload, headers=cashier_headers
            ).status_code
            == 403
        )
        assert (
            client.post(
                "/api/v1/inventory/adjust", json=payload, headers=manager_headers
            ).status_code
            == 200
        )

    def test_cashier_cannot_refund(self, client, admin_headers, cashier_headers):
        resp = client.post(
            "/api/v1/sales/refunds",
            json={
                "sale_id": "00000000-0000-0000-0000-000000000000",
                "items": [],
                "reason": "test",
            },
            headers=cashier_headers,
        )
        assert resp.status_code == 403

    def test_cashier_cannot_change_business_settings(self, client, cashier_headers):
        resp = client.patch(
            "/api/v1/settings/",
            json={"business_name": "Hacked"},
            headers=cashier_headers,
        )
        assert resp.status_code == 403

    def test_unauthenticated_request_is_rejected_everywhere(self, client):
        assert client.get("/api/v1/products/").status_code == 401
        assert client.get("/api/v1/customers/").status_code == 401
        assert client.get("/api/v1/reports/sales-summary").status_code == 401
        assert client.post("/api/v1/sales/", json={}).status_code == 401

    def test_regular_endpoints_are_open_to_every_role(
        self, client, admin_headers, manager_headers, cashier_headers
    ):
        for headers in (admin_headers, manager_headers, cashier_headers):
            assert client.get("/api/v1/products/", headers=headers).status_code == 200
            assert client.get("/api/v1/customers/", headers=headers).status_code == 200
