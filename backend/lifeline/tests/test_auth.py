import uuid

from database import sessionLocal
from lifeline.core.security import hash_secret
from lifeline.models.user import User, UserRole


class TestPasswordLogin:
    def test_login_with_correct_credentials_succeeds(self, client, admin):
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": admin["email"], "password": "password123"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["user"]["email"] == admin["email"]

    def test_login_with_wrong_password_fails(self, client, admin):
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": admin["email"], "password": "wrong-password"},
        )
        assert resp.status_code == 401

    def test_login_with_unknown_email_fails(self, client):
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": "nobody@nowhere.com", "password": "whatever"},
        )
        assert resp.status_code == 401

    def test_login_is_case_sensitive_on_password(self, client, admin):
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": admin["email"], "password": "PASSWORD123"},
        )
        assert resp.status_code == 401

    def test_inactive_user_cannot_log_in(self, client, admin, admin_headers):
        db = sessionLocal()
        user = User(
            email="inactive@test.com",
            password=hash_secret("password123"),
            role=UserRole.CASHIER.value,
            first_name="I",
            last_name="Nactive",
            is_active=False,
        )
        db.add(user)
        db.commit()
        db.close()

        resp = client.post(
            "/api/v1/auth/login",
            data={"username": "inactive@test.com", "password": "password123"},
        )
        assert resp.status_code == 403


class TestPinLogin:
    def test_pin_login_with_correct_pin_succeeds(self, client, cashier):
        resp = client.post(
            "/api/v1/auth/pin-login",
            json={"user_id": cashier["user_id"], "pin": "3333"},
        )
        assert resp.status_code == 200
        assert resp.json()["user"]["email"] == cashier["email"]

    def test_pin_login_with_wrong_pin_fails(self, client, cashier):
        resp = client.post(
            "/api/v1/auth/pin-login",
            json={"user_id": cashier["user_id"], "pin": "0000"},
        )
        assert resp.status_code == 401

    def test_pin_login_for_user_with_no_pin_set_fails(self, client, admin):
        db = sessionLocal()
        user = User(
            email="nopin@test.com",
            password=hash_secret("password123"),
            role=UserRole.CASHIER.value,
            first_name="No",
            last_name="Pin",
            pin=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = str(user.user_id)
        db.close()

        resp = client.post(
            "/api/v1/auth/pin-login", json={"user_id": user_id, "pin": "1234"}
        )
        assert resp.status_code == 401

    def test_pin_login_for_nonexistent_user_fails(self, client):
        resp = client.post(
            "/api/v1/auth/pin-login", json={"user_id": str(uuid.uuid4()), "pin": "1234"}
        )
        assert resp.status_code == 401


class TestSessionAndSwitching:
    def test_me_endpoint_requires_auth(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_me_endpoint_returns_current_user(self, client, admin_headers, admin):
        resp = client.get("/api/v1/auth/me", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == admin["email"]

    def test_garbage_token_is_rejected(self, client):
        resp = client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
        )
        assert resp.status_code == 401

    def test_switch_user_list_only_shows_active_users(self, client, admin, cashier):
        db = sessionLocal()
        inactive = User(
            email="ghost@test.com",
            password=hash_secret("x"),
            role=UserRole.CASHIER.value,
            first_name="Ghost",
            last_name="User",
            is_active=False,
        )
        db.add(inactive)
        db.commit()
        db.close()

        resp = client.get("/api/v1/auth/switch-user-list")
        assert resp.status_code == 200
        emails = [u["email"] for u in resp.json()]
        assert admin["email"] in emails
        assert cashier["email"] in emails
        assert "ghost@test.com" not in emails
