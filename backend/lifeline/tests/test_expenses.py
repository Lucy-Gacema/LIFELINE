class TestExpenses:
    def test_create_expense(self, client, admin_headers):
        resp = client.post(
            "/api/v1/expenses/",
            json={
                "category": "electricity",
                "amount": 1500,
                "payment_method": "cash",
                "note": "monthly bill",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["category"] == "electricity"

    def test_cashier_cannot_create_expense(self, client, cashier_headers):
        resp = client.post(
            "/api/v1/expenses/",
            json={"category": "transport", "amount": 100},
            headers=cashier_headers,
        )
        assert resp.status_code == 403

    def test_cashier_cannot_list_expenses(self, client, cashier_headers):
        resp = client.get("/api/v1/expenses/", headers=cashier_headers)
        assert resp.status_code == 403

    def test_missing_category_is_rejected(self, client, admin_headers):
        resp = client.post(
            "/api/v1/expenses/", json={"amount": 100}, headers=admin_headers
        )
        assert resp.status_code == 422

    def test_missing_amount_is_rejected(self, client, admin_headers):
        resp = client.post(
            "/api/v1/expenses/", json={"category": "rent"}, headers=admin_headers
        )
        assert resp.status_code == 422

    def test_negative_amount_is_rejected(self, client, admin_headers):
        resp = client.post(
            "/api/v1/expenses/",
            json={"category": "rent", "amount": -500},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_zero_amount_is_rejected(self, client, admin_headers):
        resp = client.post(
            "/api/v1/expenses/",
            json={"category": "rent", "amount": 0},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_manager_can_list_expenses(self, client, manager_headers):
        client.post(
            "/api/v1/expenses/",
            json={"category": "repairs", "amount": 500},
            headers=manager_headers,
        )
        resp = client.get("/api/v1/expenses/", headers=manager_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
