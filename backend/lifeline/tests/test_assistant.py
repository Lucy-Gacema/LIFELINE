def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_assistant_records_sale_after_confirmation(client, admin_token):
    headers = _auth_headers(admin_token)
    client.post("/api/v1/products/", json={"product_name": "Milk", "selling_price": 60, "current_stock": 20}, headers=headers)

    first = client.post(
        "/api/v1/assistant/message",
        json={"message": "I sold 2 milk"},
        headers=headers,
    )
    assert first.status_code == 200, first.text
    data = first.json()
    assert data["proposed_action"] is not None
    assert data["proposed_action"]["tool_name"] == "create_sale"

    confirm = client.post(
        "/api/v1/assistant/message",
        json={
            "message": "yes",
            "conversation_id": data["conversation_id"],
            "confirm_action_id": data["proposed_action"]["action_id"],
            "confirmed": True,
        },
        headers=headers,
    )
    assert confirm.status_code == 200, confirm.text
    assert "receipt" in confirm.json()["reply_text"].lower()


def test_assistant_sales_summary_question(client, admin_token):
    headers = _auth_headers(admin_token)
    resp = client.post("/api/v1/assistant/message", json={"message": "how much have I made today?"}, headers=headers)
    assert resp.status_code == 200
    assert "sales" in resp.json()["reply_text"].lower() or "ksh" in resp.json()["reply_text"].lower()
