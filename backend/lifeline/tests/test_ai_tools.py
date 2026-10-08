"""
Direct unit tests of the AI's tool functions (lifeline.services.ai_tools).

These bypass the LLM entirely and call the same Python functions the AI
would call — this is what actually matters for safety: regardless of which
provider (Anthropic, Gemini, or none) is wired up in ai_agent.py, every tool
must independently enforce permissions and validate input, because the
tool layer is the real security boundary, not the model's judgment.
"""

import pytest

from lifeline.models.user import User
from lifeline.services import ai_tools
from lifeline.services.ai_tools import ToolError

from .conftest import make_product


def _get_user(db_session, user_id):
    return db_session.query(User).filter(User.user_id == user_id).first()


class TestLookupProduct:
    def test_lookup_finds_exact_match(self, client, admin, admin_headers, db_session):
        make_product(client, admin_headers, product_name="Findable Milk")
        user = _get_user(db_session, admin["user_id"])
        result = ai_tools.lookup_product(db_session, user, "Findable Milk")
        assert result["found"] is True
        assert any(m["name"] == "Findable Milk" for m in result["matches"])

    def test_lookup_with_no_match_returns_found_false(self, client, admin, db_session):
        user = _get_user(db_session, admin["user_id"])
        result = ai_tools.lookup_product(
            db_session, user, "totally-nonexistent-item-zzz"
        )
        assert result["found"] is False
        assert result["matches"] == []

    def test_lookup_matches_alias(self, client, admin, admin_headers, db_session):
        make_product(
            client,
            admin_headers,
            product_name="Blue Band Margarine",
            aliases=["blueband"],
        )
        user = _get_user(db_session, admin["user_id"])
        result = ai_tools.lookup_product(db_session, user, "blueband")
        assert result["found"] is True


class TestCalculateCart:
    def test_resolves_unambiguous_items(self, client, admin, admin_headers, db_session):
        make_product(
            client,
            admin_headers,
            product_name="Unique Sugar Item",
            selling_price=150,
            current_stock=20,
        )
        user = _get_user(db_session, admin["user_id"])
        result = ai_tools.calculate_cart(
            db_session, user, [{"product_name": "Unique Sugar Item", "quantity": 2}]
        )
        assert result["total"] == 300
        assert result["not_found"] == []
        assert result["ambiguous"] == []

    def test_flags_ambiguous_matches(self, client, admin, admin_headers, db_session):
        make_product(client, admin_headers, product_name="Milk 500ml")
        make_product(client, admin_headers, product_name="Milk 1L")
        user = _get_user(db_session, admin["user_id"])
        result = ai_tools.calculate_cart(
            db_session, user, [{"product_name": "Milk", "quantity": 1}]
        )
        assert len(result["ambiguous"]) == 1
        assert len(result["ambiguous"][0]["options"]) == 2

    def test_flags_not_found_items(self, client, admin, db_session):
        user = _get_user(db_session, admin["user_id"])
        result = ai_tools.calculate_cart(
            db_session, user, [{"product_name": "nonexistent-xyz", "quantity": 1}]
        )
        assert result["not_found"] == ["nonexistent-xyz"]
        assert result["total"] == 0

    def test_empty_items_list_returns_zero_total(self, client, admin, db_session):
        user = _get_user(db_session, admin["user_id"])
        result = ai_tools.calculate_cart(db_session, user, [])
        assert result["total"] == 0
        assert result["resolved_items"] == []


class TestPermissionEnforcementInTools:
    def test_cashier_cannot_use_profit_tool(self, client, cashier, db_session):
        user = _get_user(db_session, cashier["user_id"])
        with pytest.raises(ToolError):
            ai_tools.get_profit_summary(db_session, user)

    def test_admin_can_use_profit_tool(self, client, admin, db_session):
        user = _get_user(db_session, admin["user_id"])
        result = ai_tools.get_profit_summary(db_session, user)
        assert "gross_profit" in result

    def test_cashier_cannot_adjust_inventory_via_tool(
        self, client, cashier, admin_headers, db_session
    ):
        product = make_product(client, admin_headers)
        user = _get_user(db_session, cashier["user_id"])
        with pytest.raises(ToolError):
            ai_tools.adjust_inventory(
                db_session, user, product["product_name"], 5, "restock"
            )

    def test_cashier_cannot_create_expense_via_tool(self, client, cashier, db_session):
        user = _get_user(db_session, cashier["user_id"])
        with pytest.raises(ToolError):
            ai_tools.create_expense(db_session, user, "rent", 500)

    def test_lookup_tools_have_no_permission_gate(self, client, cashier, db_session):
        # Read-only lookups are intentionally open to every role.
        user = _get_user(db_session, cashier["user_id"])
        result = ai_tools.get_low_stock_products(db_session, user)
        assert "products" in result


class TestCreateSaleViaTool:
    def test_create_sale_tool_records_a_real_sale(
        self, client, admin, admin_headers, db_session
    ):
        product = make_product(
            client, admin_headers, selling_price=100, current_stock=10
        )
        user = _get_user(db_session, admin["user_id"])
        result = ai_tools.create_sale(
            db_session,
            user,
            items=[
                {"product_id": product["product_id"], "quantity": 2, "unit_price": 100}
            ],
            payments=[{"method": "cash", "amount": 200}],
        )
        assert result["total_amount"] == 200
        assert "receipt_number" in result

    def test_create_sale_tool_respects_stock_limits(
        self, client, admin, admin_headers, db_session
    ):
        product = make_product(
            client, admin_headers, selling_price=100, current_stock=1
        )
        user = _get_user(db_session, admin["user_id"])
        with pytest.raises(Exception):
            ai_tools.create_sale(
                db_session,
                user,
                items=[
                    {
                        "product_id": product["product_id"],
                        "quantity": 5,
                        "unit_price": 100,
                    }
                ],
                payments=[{"method": "cash", "amount": 500}],
            )


class TestAdjustInventoryViaTool:
    def test_ambiguous_product_query_raises_tool_error(
        self, client, admin, admin_headers, db_session
    ):
        make_product(client, admin_headers, product_name="Milk 500ml")
        make_product(client, admin_headers, product_name="Milk 1L")
        user = _get_user(db_session, admin["user_id"])
        with pytest.raises(ToolError):
            ai_tools.adjust_inventory(db_session, user, "Milk", 5, "restock")

    def test_unknown_product_query_raises_tool_error(self, client, admin, db_session):
        user = _get_user(db_session, admin["user_id"])
        with pytest.raises(ToolError):
            ai_tools.adjust_inventory(
                db_session, user, "nonexistent-product-zzz", 5, "restock"
            )
