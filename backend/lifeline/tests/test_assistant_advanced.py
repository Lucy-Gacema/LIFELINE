"""
Additional Business Assistant coverage beyond the happy-path sale flow in
test_assistant.py: cancellation, stale/unknown confirmation ids, ambiguous
product clarification via chat, and the low-stock question.

All of this runs against the deterministic rule-based fallback (AI_PROVIDER
is forced to "none" in conftest.py) — it intentionally does NOT test live
Gemini/Anthropic responses, since those are non-deterministic, rate-limited,
and cost real money per call. If you want to smoke-test a live provider,
do that manually against a running server, not in the automated suite.
"""

from .conftest import make_product


class TestConfirmationFlow:
    def test_declining_a_proposed_sale_does_not_record_it(self, client, admin_headers):
        make_product(client, admin_headers, product_name="Bread", current_stock=10)
        first = client.post(
            "/api/v1/assistant/message",
            json={"message": "sold 1 bread"},
            headers=admin_headers,
        )
        assert first.status_code == 200
        action = first.json()["proposed_action"]
        assert action is not None

        decline = client.post(
            "/api/v1/assistant/message",
            json={
                "message": "no",
                "conversation_id": first.json()["conversation_id"],
                "confirm_action_id": action["action_id"],
                "confirmed": False,
            },
            headers=admin_headers,
        )
        assert decline.status_code == 200
        assert "cancelled" in decline.json()["reply_text"].lower()

        # Stock must be unchanged since nothing was recorded.
        products = client.get(
            "/api/v1/products/?search=Bread", headers=admin_headers
        ).json()
        assert products[0]["current_stock"] == 10

    def test_confirming_an_unknown_action_id_is_handled_gracefully(
        self, client, admin_headers
    ):
        resp = client.post(
            "/api/v1/assistant/message",
            json={
                "message": "yes",
                "confirm_action_id": "00000000-0000-0000-0000-000000000000",
                "confirmed": True,
            },
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert "nothing was changed" in resp.json()["reply_text"].lower()

    def test_confirming_the_same_action_twice_only_applies_once(
        self, client, admin_headers
    ):
        make_product(client, admin_headers, product_name="Rice", current_stock=10)
        first = client.post(
            "/api/v1/assistant/message",
            json={"message": "sold 1 rice"},
            headers=admin_headers,
        )
        action_id = first.json()["proposed_action"]["action_id"]
        conv_id = first.json()["conversation_id"]

        confirm1 = client.post(
            "/api/v1/assistant/message",
            json={
                "message": "yes",
                "conversation_id": conv_id,
                "confirm_action_id": action_id,
                "confirmed": True,
            },
            headers=admin_headers,
        )
        assert confirm1.status_code == 200
        assert "receipt" in confirm1.json()["reply_text"].lower()

        # Replaying the same action_id a second time should find nothing pending
        # (it was already popped from the pending-actions store).
        confirm2 = client.post(
            "/api/v1/assistant/message",
            json={
                "message": "yes",
                "conversation_id": conv_id,
                "confirm_action_id": action_id,
                "confirmed": True,
            },
            headers=admin_headers,
        )
        assert "nothing was changed" in confirm2.json()["reply_text"].lower()


class TestAmbiguousProductClarification:
    def test_ambiguous_product_name_asks_which_one(self, client, admin_headers):
        make_product(client, admin_headers, product_name="Milk 500ml", selling_price=60)
        make_product(client, admin_headers, product_name="Milk 1L", selling_price=110)

        resp = client.post(
            "/api/v1/assistant/message",
            json={"message": "sold 1 milk"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["requires_clarification"] is True
        assert "which" in body["reply_text"].lower()
        assert (
            body["proposed_action"] is None
        )  # must not propose a sale until disambiguated


class TestUnrecognizedInput:
    def test_unparseable_sale_sentence_asks_for_clarification_not_a_crash(
        self, client, admin_headers
    ):
        resp = client.post(
            "/api/v1/assistant/message", json={"message": "sold"}, headers=admin_headers
        )
        assert resp.status_code == 200
        assert resp.json()["requires_clarification"] is True

    def test_completely_unrelated_message_gets_a_helpful_default_reply(
        self, client, admin_headers
    ):
        resp = client.post(
            "/api/v1/assistant/message",
            json={"message": "what is the meaning of life"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()["reply_text"]) > 0

    def test_empty_message_does_not_crash(self, client, admin_headers):
        resp = client.post(
            "/api/v1/assistant/message", json={"message": ""}, headers=admin_headers
        )
        assert resp.status_code == 200


class TestLowStockQuestion:
    def test_low_stock_question_lists_low_products(self, client, admin_headers):
        make_product(
            client,
            admin_headers,
            product_name="Almost Gone",
            current_stock=1,
            minimum_stock=10,
        )
        resp = client.post(
            "/api/v1/assistant/message",
            json={"message": "what products are low on stock"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert "Almost Gone" in resp.json()["reply_text"]

    def test_low_stock_question_with_nothing_low_says_so(self, client, admin_headers):
        make_product(client, admin_headers, current_stock=100, minimum_stock=5)
        resp = client.post(
            "/api/v1/assistant/message",
            json={"message": "any low stock items"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert "nothing" in resp.json()["reply_text"].lower()
