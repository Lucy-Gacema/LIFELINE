import uuid
from .conftest import make_product


class TestSuppliers:
    def test_create_supplier(self, client, admin_headers):
        resp = client.post("/api/v1/suppliers/", json={"name": "Acme Wholesale", "phone": "0700000000"}, headers=admin_headers)
        assert resp.status_code == 201
        assert resp.json()["name"] == "Acme Wholesale"

    def test_missing_name_is_rejected(self, client, admin_headers):
        resp = client.post("/api/v1/suppliers/", json={"phone": "0700000000"}, headers=admin_headers)
        assert resp.status_code == 422

    def test_cashier_cannot_create_supplier(self, client, cashier_headers):
        resp = client.post("/api/v1/suppliers/", json={"name": "X"}, headers=cashier_headers)
        assert resp.status_code == 403

    def test_get_nonexistent_supplier_returns_404(self, client, admin_headers):
        resp = client.get(f"/api/v1/suppliers/{uuid.uuid4()}", headers=admin_headers)
        assert resp.status_code == 404

    def test_list_suppliers_is_sorted_by_name(self, client, admin_headers):
        client.post("/api/v1/suppliers/", json={"name": "Zeta Supplies"}, headers=admin_headers)
        client.post("/api/v1/suppliers/", json={"name": "Alpha Supplies"}, headers=admin_headers)
        resp = client.get("/api/v1/suppliers/", headers=admin_headers)
        names = [s["name"] for s in resp.json()]
        assert names == sorted(names)


class TestPurchaseOrders:
    def test_create_purchase_order(self, client, admin_headers):
        supplier = client.post("/api/v1/suppliers/", json={"name": "PO Supplier"}, headers=admin_headers).json()
        product = make_product(client, admin_headers)

        resp = client.post(
            f"/api/v1/suppliers/purchase-orders?supplier_id={supplier['supplier_id']}",
            json=[{"product_id": product["product_id"], "quantity_ordered": 50, "unit_cost": 80}],
            headers=admin_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["status"] == "ordered"


class TestReorderPlanner:
    def test_reorder_planner_lists_low_stock_products(self, client, admin_headers):
        low = make_product(client, admin_headers, current_stock=1, minimum_stock=10)
        healthy = make_product(client, admin_headers, current_stock=100, minimum_stock=10)

        resp = client.get("/api/v1/suppliers/reorder-planner/list", headers=admin_headers)
        assert resp.status_code == 200
        ids = [r["product_id"] for r in resp.json()]
        assert low["product_id"] in ids
        assert healthy["product_id"] not in ids

    def test_reorder_quantity_is_never_negative(self, client, admin_headers):
        product = make_product(client, admin_headers, current_stock=9, minimum_stock=10, maximum_stock=15)
        resp = client.get("/api/v1/suppliers/reorder-planner/list", headers=admin_headers)
        entry = next(r for r in resp.json() if r["product_id"] == product["product_id"])
        assert entry["suggested_reorder_quantity"] >= 0
