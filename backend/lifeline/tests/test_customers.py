import uuid
from .conftest import make_customer


class TestCustomerCreation:
    def test_create_with_name_only(self, client, admin_headers):
        resp = client.post("/api/v1/customers/", json={"name": "Jane Doe"}, headers=admin_headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "Jane Doe"
        assert float(body["outstanding_balance"]) == 0

    def test_empty_name_is_rejected(self, client, admin_headers):
        resp = client.post("/api/v1/customers/", json={"name": ""}, headers=admin_headers)
        assert resp.status_code == 422

    def test_missing_name_is_rejected(self, client, admin_headers):
        resp = client.post("/api/v1/customers/", json={"phone": "0700000000"}, headers=admin_headers)
        assert resp.status_code == 422

    def test_create_with_phone_and_email(self, client, admin_headers):
        resp = client.post(
            "/api/v1/customers/", json={"name": "John", "phone": "0712345678", "email": "john@test.com"},
            headers=admin_headers,
        )
        assert resp.status_code == 201


class TestCustomerSearch:
    def test_search_by_partial_name_is_case_insensitive(self, client, admin_headers):
        make_customer(client, admin_headers, name="Alice Wonderland")
        resp = client.get("/api/v1/customers/?search=alice", headers=admin_headers)
        assert resp.status_code == 200
        assert any("Alice" in c["name"] for c in resp.json())

    def test_search_by_partial_phone(self, client, admin_headers):
        make_customer(client, admin_headers, name="Phone Person", phone="0798765432")
        resp = client.get("/api/v1/customers/?search=9876", headers=admin_headers)
        assert resp.status_code == 200
        assert any(c["phone"] == "0798765432" for c in resp.json())

    def test_search_with_no_match_returns_empty(self, client, admin_headers):
        resp = client.get("/api/v1/customers/?search=zzz-nobody-zzz", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json() == []


class TestCustomerUpdate:
    def test_update_phone_number(self, client, admin_headers):
        customer = make_customer(client, admin_headers)
        resp = client.patch(f"/api/v1/customers/{customer['customer_id']}", json={"phone": "0711111111"}, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["phone"] == "0711111111"

    def test_update_nonexistent_customer_returns_404(self, client, admin_headers):
        resp = client.patch(f"/api/v1/customers/{uuid.uuid4()}", json={"phone": "0700000000"}, headers=admin_headers)
        assert resp.status_code == 404

    def test_get_nonexistent_customer_returns_404(self, client, admin_headers):
        resp = client.get(f"/api/v1/customers/{uuid.uuid4()}", headers=admin_headers)
        assert resp.status_code == 404

    def test_cashier_can_read_but_manager_permission_needed_to_update(self, client, cashier_headers):
        create_resp = client.post("/api/v1/customers/", json={"name": "Cashier Created"}, headers=cashier_headers)
        assert create_resp.status_code == 201
        customer_id = create_resp.json()["customer_id"]

        update_resp = client.patch(f"/api/v1/customers/{customer_id}", json={"phone": "0700"}, headers=cashier_headers)
        assert update_resp.status_code == 403
