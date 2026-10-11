import uuid
from .conftest import make_product, make_sale


class TestShiftOpening:
    def test_open_shift_succeeds(self, client, admin_headers):
        resp = client.post("/api/v1/shifts/open", json={"opening_cash": 500}, headers=admin_headers)
        assert resp.status_code == 201
        assert float(resp.json()["opening_cash"]) == 500
        assert resp.json()["status"] == "open"

    def test_open_shift_with_zero_cash_is_allowed(self, client, admin_headers):
        resp = client.post("/api/v1/shifts/open", json={"opening_cash": 0}, headers=admin_headers)
        assert resp.status_code == 201

    def test_open_shift_with_negative_cash_is_rejected(self, client, admin_headers):
        resp = client.post("/api/v1/shifts/open", json={"opening_cash": -100}, headers=admin_headers)
        assert resp.status_code == 422

    def test_cannot_open_a_second_shift_while_one_is_open(self, client, admin_headers):
        client.post("/api/v1/shifts/open", json={"opening_cash": 100}, headers=admin_headers)
        second = client.post("/api/v1/shifts/open", json={"opening_cash": 200}, headers=admin_headers)
        assert second.status_code == 400

    def test_current_shift_returns_404_when_none_open(self, client, cashier_headers):
        resp = client.get("/api/v1/shifts/current", headers=cashier_headers)
        assert resp.status_code == 404

    def test_current_shift_returns_the_open_one(self, client, admin_headers):
        opened = client.post("/api/v1/shifts/open", json={"opening_cash": 300}, headers=admin_headers).json()
        current = client.get("/api/v1/shifts/current", headers=admin_headers)
        assert current.status_code == 200
        assert current.json()["shift_id"] == opened["shift_id"]


class TestCashMovementsAndExpectedCash:
    def test_expected_cash_includes_cash_sales(self, client, admin_headers):
        shift = client.post("/api/v1/shifts/open", json={"opening_cash": 1000}, headers=admin_headers).json()
        product = make_product(client, admin_headers, selling_price=200, current_stock=10)
        make_sale(
            client, admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 1}],
            payments=[{"method": "cash", "amount": 200}],
            shift_id=shift["shift_id"],
        )

        resp = client.get(f"/api/v1/shifts/{shift['shift_id']}/expected-cash", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["expected_cash"] == 1200

    def test_expected_cash_excludes_non_cash_sales(self, client, admin_headers):
        shift = client.post("/api/v1/shifts/open", json={"opening_cash": 1000}, headers=admin_headers).json()
        product = make_product(client, admin_headers, selling_price=500, current_stock=10)
        make_sale(
            client, admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 1}],
            payments=[{"method": "mpesa", "amount": 500}],
            shift_id=shift["shift_id"],
        )
        resp = client.get(f"/api/v1/shifts/{shift['shift_id']}/expected-cash", headers=admin_headers)
        assert resp.json()["expected_cash"] == 1000

    def test_cash_drop_reduces_expected_cash(self, client, admin_headers):
        shift = client.post("/api/v1/shifts/open", json={"opening_cash": 1000}, headers=admin_headers).json()
        client.post(f"/api/v1/shifts/{shift['shift_id']}/cash-movement", json={"type": "drop", "amount": 300, "reason": "bank deposit"}, headers=admin_headers)
        resp = client.get(f"/api/v1/shifts/{shift['shift_id']}/expected-cash", headers=admin_headers)
        assert resp.json()["expected_cash"] == 700

    def test_cash_movement_on_nonexistent_shift_returns_404(self, client, admin_headers):
        resp = client.post(f"/api/v1/shifts/{uuid.uuid4()}/cash-movement", json={"type": "drop", "amount": 100}, headers=admin_headers)
        assert resp.status_code == 404

    def test_invalid_cash_movement_type_is_rejected(self, client, admin_headers):
        shift = client.post("/api/v1/shifts/open", json={"opening_cash": 100}, headers=admin_headers).json()
        resp = client.post(f"/api/v1/shifts/{shift['shift_id']}/cash-movement", json={"type": "steal_money", "amount": 50}, headers=admin_headers)
        assert resp.status_code == 422


class TestShiftClosing:
    def test_close_shift_with_matching_cash_has_zero_difference(self, client, admin_headers):
        shift = client.post("/api/v1/shifts/open", json={"opening_cash": 500}, headers=admin_headers).json()
        resp = client.post(f"/api/v1/shifts/{shift['shift_id']}/close", json={"actual_cash": 500}, headers=admin_headers)
        assert resp.status_code == 200
        assert float(resp.json()["cash_difference"]) == 0
        assert resp.json()["status"] == "closed"

    def test_close_shift_with_shortfall_records_negative_difference(self, client, admin_headers):
        shift = client.post("/api/v1/shifts/open", json={"opening_cash": 500}, headers=admin_headers).json()
        resp = client.post(f"/api/v1/shifts/{shift['shift_id']}/close", json={"actual_cash": 470, "closing_note": "short by 30"}, headers=admin_headers)
        assert resp.status_code == 200
        assert float(resp.json()["cash_difference"]) == -30

    def test_closing_an_already_closed_shift_fails(self, client, admin_headers):
        shift = client.post("/api/v1/shifts/open", json={"opening_cash": 500}, headers=admin_headers).json()
        client.post(f"/api/v1/shifts/{shift['shift_id']}/close", json={"actual_cash": 500}, headers=admin_headers)
        second = client.post(f"/api/v1/shifts/{shift['shift_id']}/close", json={"actual_cash": 500}, headers=admin_headers)
        assert second.status_code == 400

    def test_closing_nonexistent_shift_returns_404(self, client, admin_headers):
        resp = client.post(f"/api/v1/shifts/{uuid.uuid4()}/close", json={"actual_cash": 0}, headers=admin_headers)
        assert resp.status_code == 404
