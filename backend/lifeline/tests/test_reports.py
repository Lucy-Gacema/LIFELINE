from .conftest import make_product, make_sale


class TestSalesSummary:
    def test_zero_sales_gives_zero_totals_not_an_error(self, client, admin_headers):
        resp = client.get(
            "/api/v1/reports/sales-summary?period=today", headers=admin_headers
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_sales"] == 0
        assert body["transaction_count"] == 0
        assert body["average_transaction"] == 0

    def test_sales_summary_reflects_completed_sales(self, client, admin_headers):
        product = make_product(
            client, admin_headers, selling_price=100, current_stock=10
        )
        make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 2}],
            payments=[{"method": "cash", "amount": 200}],
        )

        resp = client.get(
            "/api/v1/reports/sales-summary?period=today", headers=admin_headers
        )
        body = resp.json()
        assert body["total_sales"] == 200
        assert body["transaction_count"] == 1

    def test_voided_sale_is_excluded_from_summary(self, client, admin_headers):
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
            f"/api/v1/sales/{sale['sale_id']}/void?reason=test", headers=admin_headers
        )

        resp = client.get(
            "/api/v1/reports/sales-summary?period=today", headers=admin_headers
        )
        assert resp.json()["transaction_count"] == 0

    def test_invalid_period_falls_back_gracefully(self, client, admin_headers):
        resp = client.get(
            "/api/v1/reports/sales-summary?period=not-a-real-period",
            headers=admin_headers,
        )
        assert resp.status_code == 200


class TestProfitSummary:
    def test_cashier_forbidden(self, client, cashier_headers):
        resp = client.get("/api/v1/reports/profit-summary", headers=cashier_headers)
        assert resp.status_code == 403

    def test_profit_is_revenue_minus_cost(self, client, admin_headers):
        product = make_product(
            client, admin_headers, selling_price=100, buying_price=60, current_stock=10
        )
        make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 2}],
            payments=[{"method": "cash", "amount": 200}],
        )

        resp = client.get(
            "/api/v1/reports/profit-summary?period=today", headers=admin_headers
        )
        body = resp.json()
        assert body["revenue"] == 200
        assert body["estimated_cost"] == 120
        assert body["gross_profit"] == 80

    def test_product_with_no_buying_price_treated_as_zero_cost(
        self, client, admin_headers
    ):
        product = make_product(
            client, admin_headers, selling_price=50, current_stock=10
        )
        make_sale(
            client,
            admin_headers,
            items=[{"product_id": product["product_id"], "quantity": 1}],
            payments=[{"method": "cash", "amount": 50}],
        )

        resp = client.get(
            "/api/v1/reports/profit-summary?period=today", headers=admin_headers
        )
        assert resp.json()["gross_profit"] == 50


class TestTopProducts:
    def test_top_products_ranked_by_quantity(self, client, admin_headers):
        best = make_product(client, admin_headers, selling_price=10, current_stock=100)
        worst = make_product(client, admin_headers, selling_price=10, current_stock=100)
        make_sale(
            client,
            admin_headers,
            items=[{"product_id": best["product_id"], "quantity": 10}],
            payments=[{"method": "cash", "amount": 100}],
        )
        make_sale(
            client,
            admin_headers,
            items=[{"product_id": worst["product_id"], "quantity": 1}],
            payments=[{"method": "cash", "amount": 10}],
        )

        resp = client.get(
            "/api/v1/reports/top-products?period=today&by=quantity",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        names = [p["name"] for p in resp.json()]
        assert names[0] == best["product_name"]

    def test_top_products_with_no_sales_is_empty_list(self, client, admin_headers):
        resp = client.get(
            "/api/v1/reports/top-products?period=today", headers=admin_headers
        )
        assert resp.status_code == 200
        assert resp.json() == []


class TestBusinessHealth:
    def test_business_health_accessible_to_cashier(self, client, cashier_headers):
        resp = client.get("/api/v1/reports/business-health", headers=cashier_headers)
        assert resp.status_code == 200
        assert "today" in resp.json()

    def test_business_health_includes_low_stock_products(self, client, admin_headers):
        low = make_product(client, admin_headers, current_stock=1, minimum_stock=10)
        resp = client.get("/api/v1/reports/business-health", headers=admin_headers)
        ids = [p["product_id"] for p in resp.json()["low_stock_products"]]
        assert low["product_id"] in ids
