import uuid

from .conftest import make_product, make_sale


def _make_completed_sale(client, headers, quantity=3, price=100):
    product = make_product(client, headers, selling_price=price, current_stock=20)
    sale = make_sale(
        client,
        headers,
        items=[{"product_id": product["product_id"], "quantity": quantity}],
        payments=[{"method": "cash", "amount": price * quantity}],
    ).json()
    return product, sale


class TestRefunds:
    def test_full_refund_restocks_and_marks_sale_refunded(self, client, admin_headers):
        product, sale = _make_completed_sale(
            client, admin_headers, quantity=2, price=100
        )
        sale_item_id = sale["items"][0]["sale_item_id"]

        resp = client.post(
            "/api/v1/sales/refunds",
            json={
                "sale_id": sale["sale_id"],
                "items": [{"sale_item_id": sale_item_id, "quantity": 2}],
                "reason": "customer return",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        assert float(resp.json()["total_amount"]) == 200

        updated_sale = client.get(
            f"/api/v1/sales/{sale['sale_id']}", headers=admin_headers
        ).json()
        assert updated_sale["status"] == "refunded"

        updated_product = client.get(
            f"/api/v1/products/{product['product_id']}", headers=admin_headers
        ).json()
        assert updated_product["current_stock"] == 20

    def test_partial_refund_marks_sale_partially_refunded(self, client, admin_headers):
        product, sale = _make_completed_sale(
            client, admin_headers, quantity=4, price=50
        )
        sale_item_id = sale["items"][0]["sale_item_id"]

        resp = client.post(
            "/api/v1/sales/refunds",
            json={
                "sale_id": sale["sale_id"],
                "items": [{"sale_item_id": sale_item_id, "quantity": 1}],
                "reason": "one item damaged",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        assert float(resp.json()["total_amount"]) == 50

        updated_sale = client.get(
            f"/api/v1/sales/{sale['sale_id']}", headers=admin_headers
        ).json()
        assert updated_sale["status"] == "partially_refunded"

    def test_refund_more_than_purchased_is_blocked(self, client, admin_headers):
        product, sale = _make_completed_sale(
            client, admin_headers, quantity=2, price=100
        )
        sale_item_id = sale["items"][0]["sale_item_id"]

        resp = client.post(
            "/api/v1/sales/refunds",
            json={
                "sale_id": sale["sale_id"],
                "items": [{"sale_item_id": sale_item_id, "quantity": 5}],
                "reason": "test",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 400

    def test_refunding_twice_beyond_original_quantity_is_blocked(
        self, client, admin_headers
    ):
        product, sale = _make_completed_sale(
            client, admin_headers, quantity=3, price=100
        )
        sale_item_id = sale["items"][0]["sale_item_id"]

        first = client.post(
            "/api/v1/sales/refunds",
            json={
                "sale_id": sale["sale_id"],
                "items": [{"sale_item_id": sale_item_id, "quantity": 2}],
                "reason": "first",
            },
            headers=admin_headers,
        )
        assert first.status_code == 201

        second = client.post(
            "/api/v1/sales/refunds",
            json={
                "sale_id": sale["sale_id"],
                "items": [{"sale_item_id": sale_item_id, "quantity": 2}],
                "reason": "second",
            },
            headers=admin_headers,
        )
        assert second.status_code == 400

    def test_refund_on_nonexistent_sale_returns_404(self, client, admin_headers):
        resp = client.post(
            "/api/v1/sales/refunds",
            json={"sale_id": str(uuid.uuid4()), "items": [], "reason": "test"},
            headers=admin_headers,
        )
        assert resp.status_code == 404

    def test_refund_zero_quantity_is_rejected(self, client, admin_headers):
        product, sale = _make_completed_sale(
            client, admin_headers, quantity=1, price=100
        )
        sale_item_id = sale["items"][0]["sale_item_id"]
        resp = client.post(
            "/api/v1/sales/refunds",
            json={
                "sale_id": sale["sale_id"],
                "items": [{"sale_item_id": sale_item_id, "quantity": 0}],
                "reason": "test",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_manager_can_refund_cashier_cannot(
        self, client, manager_headers, cashier_headers, admin_headers
    ):
        product, sale = _make_completed_sale(
            client, admin_headers, quantity=1, price=100
        )
        sale_item_id = sale["items"][0]["sale_item_id"]

        cashier_resp = client.post(
            "/api/v1/sales/refunds",
            json={
                "sale_id": sale["sale_id"],
                "items": [{"sale_item_id": sale_item_id, "quantity": 1}],
                "reason": "x",
            },
            headers=cashier_headers,
        )
        assert cashier_resp.status_code == 403

        manager_resp = client.post(
            "/api/v1/sales/refunds",
            json={
                "sale_id": sale["sale_id"],
                "items": [{"sale_item_id": sale_item_id, "quantity": 1}],
                "reason": "x",
            },
            headers=manager_headers,
        )
        assert manager_resp.status_code == 201
