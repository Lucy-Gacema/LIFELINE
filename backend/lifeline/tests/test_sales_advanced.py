import uuid
 
from .conftest import make_customer, make_product, make_sale
 
 
class TestMultiItemAndDiscounts:
    def test_sale_with_multiple_items_totals_correctly(self, client, admin_headers):
        p1 = make_product(client, admin_headers, selling_price=50, current_stock=10)
        p2 = make_product(client, admin_headers, selling_price=30, current_stock=10)
 
        resp = make_sale(
            client,
            admin_headers,
            items=[
                {"product_id": p1["product_id"], "quantity": 2},
                {"product_id": p2["product_id"], "quantity": 3},
            ],
            payments=[{"method": "cash", "amount": 190}],
        )
        assert resp.status_code == 201
        body = resp.json()
        assert float(body["subtotal"]) == 190
        assert float(body["total_amount"]) == 190
 
    def test_discount_reduces_total(self, client, admin_headers):
        product = make_product(
            client, admin_headers, selling_price=100, current_stock=10
        )
        resp = make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 1}],
            payments=[{"method": "cash", "amount": 80}],
            discount_total=20,
        )
        assert resp.status_code == 201
        assert float(resp.json()["total_amount"]) == 80
 
    def test_manual_item_with_no_catalog_product_requires_explicit_price(
        self, client, admin_headers
    ):
        resp = make_sale(
            client,
            admin_headers,
            items=[{"product_name": "Custom bag of nails", "quantity": 1}],
            payments=[{"method": "cash", "amount": 100}],
        )
        assert resp.status_code == 400
 
    def test_manual_item_with_explicit_price_succeeds(self, client, admin_headers):
        resp = make_sale(
            client,
            admin_headers,
            items=[
                {
                    "product_name": "Custom bag of nails",
                    "quantity": 1,
                    "unit_price": 250,
                }
            ],
            payments=[{"method": "cash", "amount": 250}],
        )
        assert resp.status_code == 201
        assert float(resp.json()["total_amount"]) == 250
 
 
class TestSplitPayments:
    def test_split_between_cash_and_mpesa(self, client, admin_headers):
        product = make_product(
            client, admin_headers, selling_price=1000, current_stock=10
        )
        resp = make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 1}],
            payments=[
                {"method": "mpesa", "amount": 600},
                {"method": "cash", "amount": 400, "amount_tendered": 400},
            ],
        )
        assert resp.status_code == 201
        assert len(resp.json()["payments"]) == 2
 
    def test_cash_change_is_calculated(self, client, admin_headers):
        product = make_product(
            client, admin_headers, selling_price=780, current_stock=10
        )
        resp = make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 1}],
            payments=[{"method": "cash", "amount": 780, "amount_tendered": 1000}],
        )
        assert resp.status_code == 201
        assert float(resp.json()["payments"][0]["change_given"]) == 220
 
 
class TestCustomerCredit:
    def test_underpayment_with_customer_goes_on_credit(self, client, admin_headers):
        product = make_product(
            client, admin_headers, selling_price=500, current_stock=10
        )
        customer = make_customer(client, admin_headers)
 
        resp = make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 1}],
            payments=[{"method": "cash", "amount": 300}],
            customer_id=customer["customer_id"],
        )
        assert resp.status_code == 201
 
        updated_customer = client.get(
            f"/api/v1/customers/{customer['customer_id']}", headers=admin_headers
        ).json()
        assert float(updated_customer["outstanding_balance"]) == 200
 
    def test_underpayment_without_customer_is_rejected(self, client, admin_headers):
        product = make_product(
            client, admin_headers, selling_price=500, current_stock=10
        )
        resp = make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 1}],
            payments=[{"method": "cash", "amount": 300}],
        )
        assert resp.status_code == 400
 
 
class TestSaleValidationBoundaries:
    def test_empty_items_list_is_rejected(self, client, admin_headers):
        resp = make_sale(
            client, admin_headers, items=[], payments=[{"method": "cash", "amount": 0}]
        )
        assert resp.status_code in (400, 422)
 
    def test_zero_quantity_item_is_rejected(self, client, admin_headers):
        product = make_product(client, admin_headers)
        resp = make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 0}],
            payments=[{"method": "cash", "amount": 0}],
        )
        assert resp.status_code == 422
 
    def test_negative_quantity_is_rejected(self, client, admin_headers):
        product = make_product(client, admin_headers)
        resp = make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": -1}],
            payments=[{"method": "cash", "amount": 100}],
        )
        assert resp.status_code == 422
 
    def test_negative_payment_amount_is_rejected(self, client, admin_headers):
        product = make_product(client, admin_headers, selling_price=100)
        resp = make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 1}],
            payments=[{"method": "cash", "amount": -100}],
        )
        assert resp.status_code == 422
 
    def test_invalid_payment_method_is_rejected(self, client, admin_headers):
        product = make_product(client, admin_headers, selling_price=100)
        resp = make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 1}],
            payments=[{"method": "bitcoin", "amount": 100}],
        )
        assert resp.status_code == 422
 
    def test_nonexistent_product_id_returns_404(self, client, admin_headers):
        resp = make_sale(
            client,
            admin_headers,
            items=[{"product_id": str(uuid.uuid4()), "quantity": 1}],
            payments=[{"method": "cash", "amount": 100}],
        )
        assert resp.status_code == 404
 
    def test_overpayment_succeeds_without_creating_negative_change_elsewhere(
        self, client, admin_headers
    ):
        product = make_product(
            client, admin_headers, selling_price=100, current_stock=5
        )
        resp = make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 1}],
            payments=[{"method": "mpesa", "amount": 150}],
        )
        assert resp.status_code == 201
 
 
class TestVoidSale:
    def test_void_restores_stock(self, client, admin_headers):
        product = make_product(
            client, admin_headers, selling_price=100, current_stock=10
        )
        sale = make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 3}],
            payments=[{"method": "cash", "amount": 300}],
        ).json()
 
        after_sale = client.get(
            f"/api/v1/products/{product['product_id']}", headers=admin_headers
        ).json()
        assert after_sale["current_stock"] == 7
 
        void_resp = client.post(
            f"/api/v1/sales/{sale['sale_id']}/void?reason=customer changed mind",
            headers=admin_headers,
        )
        assert void_resp.status_code == 200
        assert void_resp.json()["status"] == "cancelled"
 
        after_void = client.get(
            f"/api/v1/products/{product['product_id']}", headers=admin_headers
        ).json()
        assert after_void["current_stock"] == 10
 
    def test_voiding_an_already_voided_sale_fails(self, client, admin_headers):
        product = make_product(
            client, admin_headers, selling_price=100, current_stock=10
        )
        sale = make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 1}],
            payments=[{"method": "cash", "amount": 100}],
        ).json()
 
        client.post(
            f"/api/v1/sales/{sale['sale_id']}/void?reason=first void",
            headers=admin_headers,
        )
        second = client.post(
            f"/api/v1/sales/{sale['sale_id']}/void?reason=second void",
            headers=admin_headers,
        )
        assert second.status_code == 400
 
    def test_cashier_cannot_void_without_permission(
        self, client, admin_headers, cashier_headers
    ):
        product = make_product(
            client, admin_headers, selling_price=100, current_stock=10
        )
        sale = make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 1}],
            payments=[{"method": "cash", "amount": 100}],
        ).json()
 
        resp = client.post(
            f"/api/v1/sales/{sale['sale_id']}/void?reason=test", headers=cashier_headers
        )
        assert resp.status_code == 403