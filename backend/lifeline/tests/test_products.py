from .conftest import make_product

class TestProductCreation:
    def test_create_with_only_required_fields(self, client, admin_headers):
        resp = client.post(
            "/api/v1/products/",
            json={
                "product_name": "Bare Minimum",
                "selling_price": 50,
                "current_stock": 10,
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["product_name"] == "Bare Minimum"
        assert body["unit"] == "pc"
        assert body["is_active"] is True

    def test_create_with_all_optional_fields(self, client, admin_headers):
        resp = client.post(
            "/api/v1/products/",
            json={
                "product_name": "Full Product",
                "selling_price": 200,
                "current_stock": 20,
                "sku": "SKU-001",
                "barcode": "1234567890",
                "unit": "kg",
                "buying_price": 150,
                "tax_rate": 16,
                "minimum_stock": 5,
                "aliases": ["fullprod", "fp"],
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["sku"] == "SKU-001"
        assert body["aliases"] == ["fullprod", "fp"]

    def test_missing_required_name_is_rejected(self, client, admin_headers):
        resp = client.post(
            "/api/v1/products/",
            json={"selling_price": 50, "current_stock": 1},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_missing_required_price_is_rejected(self, client, admin_headers):
        resp = client.post(
            "/api/v1/products/",
            json={"product_name": "No Price"},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_empty_name_is_rejected(self, client, admin_headers):
        resp = client.post(
            "/api/v1/products/",
            json={"product_name": "", "selling_price": 10},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_zero_price_is_rejected(self, client, admin_headers):
        resp = client.post(
            "/api/v1/products/",
            json={"product_name": "Free?", "selling_price": 0},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_negative_price_is_rejected(self, client, admin_headers):
        resp = client.post(
            "/api/v1/products/",
            json={"product_name": "Negative", "selling_price": -10},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_negative_starting_stock_is_rejected(self, client, admin_headers):
        resp = client.post(
            "/api/v1/products/",
            json={
                "product_name": "Neg Stock",
                "selling_price": 10,
                "current_stock": -5,
            },
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_smallest_valid_price_is_accepted(self, client, admin_headers):
        resp = client.post(
            "/api/v1/products/",
            json={
                "product_name": "Cent Item",
                "selling_price": 0.01,
                "current_stock": 1,
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201

    def test_tax_rate_over_100_percent_is_rejected(self, client, admin_headers):
        resp = client.post(
            "/api/v1/products/",
            json={"product_name": "Weird Tax", "selling_price": 10, "tax_rate": 150},
            headers=admin_headers,
        )
        assert resp.status_code == 422


class TestProductSearch:
    def test_search_matches_partial_name(self, client, admin_headers):
        make_product(client, admin_headers, product_name="Blue Band Margarine")
        resp = client.get("/api/v1/products/search?q=blue", headers=admin_headers)
        assert resp.status_code == 200
        assert any("Blue Band" in p["product_name"] for p in resp.json())

    def test_search_matches_alias(self, client, admin_headers):
        make_product(
            client,
            admin_headers,
            product_name="Blue Band Margarine",
            aliases=["blueband", "margarine"],
        )
        resp = client.get("/api/v1/products/search?q=margarine", headers=admin_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_search_matches_sku(self, client, admin_headers):
        make_product(client, admin_headers, sku="UNIQUE-SKU-42")
        resp = client.get(
            "/api/v1/products/search?q=UNIQUE-SKU-42", headers=admin_headers
        )
        assert resp.status_code == 200
        assert any(p["sku"] == "UNIQUE-SKU-42" for p in resp.json())

    def test_search_with_no_matches_returns_empty_list(self, client, admin_headers):
        resp = client.get(
            "/api/v1/products/search?q=zzz-nonexistent-zzz", headers=admin_headers
        )
        assert resp.status_code == 200
        assert resp.json() == []

    def test_search_excludes_inactive_products(self, client, admin_headers):
        product = make_product(client, admin_headers, product_name="Soon Deleted")
        client.delete(
            f"/api/v1/products/{product['product_id']}", headers=admin_headers
        )
        resp = client.get(
            "/api/v1/products/search?q=Soon Deleted", headers=admin_headers
        )
        assert all(p["product_id"] != product["product_id"] for p in resp.json())


class TestStockStatus:
    def test_stock_above_minimum_is_healthy(self, client, admin_headers):
        product = make_product(
            client, admin_headers, current_stock=50, minimum_stock=10
        )
        assert product["stock_status"] == "healthy"

    def test_stock_at_zero_is_out_of_stock(self, client, admin_headers):
        product = make_product(client, admin_headers, current_stock=0, minimum_stock=5)
        assert product["stock_status"] == "out_of_stock"

    def test_stock_exactly_at_minimum_is_low_or_critical_not_healthy(
        self, client, admin_headers
    ):
        product = make_product(
            client, admin_headers, current_stock=10, minimum_stock=10
        )
        assert product["stock_status"] in ("low", "critical")

    def test_low_stock_endpoint_lists_only_at_or_below_minimum(
        self, client, admin_headers
    ):
        healthy = make_product(
            client, admin_headers, current_stock=100, minimum_stock=5
        )
        low = make_product(client, admin_headers, current_stock=2, minimum_stock=5)
        resp = client.get("/api/v1/products/low-stock", headers=admin_headers)
        ids = [p["product_id"] for p in resp.json()]
        assert low["product_id"] in ids
        assert healthy["product_id"] not in ids


class TestProductUpdateAndDelete:
    def test_update_price_only(self, client, admin_headers):
        product = make_product(client, admin_headers, selling_price=100)
        resp = client.patch(
            f"/api/v1/products/{product['product_id']}",
            json={"selling_price": 150},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert float(resp.json()["selling_price"]) == 150

    def test_update_with_negative_price_is_rejected(self, client, admin_headers):
        product = make_product(client, admin_headers)
        resp = client.patch(
            f"/api/v1/products/{product['product_id']}",
            json={"selling_price": -1},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_update_nonexistent_product_returns_404(self, client, admin_headers):
        resp = client.patch(
            "/api/v1/products/00000000-0000-0000-0000-000000000000",
            json={"selling_price": 1},
            headers=admin_headers,
        )
        assert resp.status_code == 404

    def test_delete_is_soft_not_hard(self, client, admin_headers):
        product = make_product(client, admin_headers)
        resp = client.delete(
            f"/api/v1/products/{product['product_id']}", headers=admin_headers
        )
        assert resp.status_code == 204
        get_resp = client.get(
            f"/api/v1/products/{product['product_id']}", headers=admin_headers
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["is_active"] is False
        list_resp = client.get("/api/v1/products/", headers=admin_headers)
        assert all(p["product_id"] != product["product_id"] for p in list_resp.json())

    def test_deleting_nonexistent_product_returns_404(self, client, admin_headers):
        resp = client.delete(
            "/api/v1/products/00000000-0000-0000-0000-000000000000",
            headers=admin_headers,
        )
        assert resp.status_code == 404


class TestCategories:
    def test_create_and_list_category(self, client, admin_headers):
        resp = client.post(
            "/api/v1/products/categories/",
            json={"name": "Beverages", "icon": "🥤"},
            headers=admin_headers,
        )
        assert resp.status_code == 201
        list_resp = client.get("/api/v1/products/categories/", headers=admin_headers)
        assert any(c["name"] == "Beverages" for c in list_resp.json())

    def test_cashier_cannot_create_category(self, client, cashier_headers):
        resp = client.post(
            "/api/v1/products/categories/",
            json={"name": "X"},
            headers=cashier_headers,
        )
        assert resp.status_code == 403
