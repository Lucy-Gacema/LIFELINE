class TestSettings:
    def test_defaults_are_returned_when_nothing_has_been_set(
        self, client, admin_headers
    ):
        resp = client.get("/api/v1/settings/", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["business_name"] == "My Shop"
        assert body["currency"] == "KES"

    def test_cashier_cannot_change_settings(self, client, cashier_headers):
        resp = client.patch(
            "/api/v1/settings/",
            json={"business_name": "New Name"},
            headers=cashier_headers,
        )
        assert resp.status_code == 403

    def test_cashier_can_still_read_settings(self, client, cashier_headers):
        resp = client.get("/api/v1/settings/", headers=cashier_headers)
        assert resp.status_code == 200

    def test_admin_can_update_business_name(self, client, admin_headers):
        resp = client.patch(
            "/api/v1/settings/",
            json={"business_name": "Jane's Shop"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["business_name"] == "Jane's Shop"

    def test_partial_update_does_not_reset_other_fields(self, client, admin_headers):
        client.patch(
            "/api/v1/settings/",
            json={"business_name": "Persistent Name"},
            headers=admin_headers,
        )
        client.patch(
            "/api/v1/settings/", json={"low_stock_threshold": 3}, headers=admin_headers
        )

        resp = client.get("/api/v1/settings/", headers=admin_headers)
        body = resp.json()
        assert body["business_name"] == "Persistent Name"
        assert body["low_stock_threshold"] == 3
