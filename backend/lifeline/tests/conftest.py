"""
Shared pytest fixtures for the whole Lifeline test suite.

Design choices worth knowing:
- Every test run gets a throwaway SQLite file (never your real lifeline.db).
- AI_PROVIDER is forced to "none" so the assistant tests exercise the
  deterministic rule-based fallback rather than hitting a live LLM API
  (paid, rate-limited, and non-deterministic — all wrong for a test suite).
  If you've switched providers (e.g. to Gemini) in your own .env, that's
  irrelevant here: this env var is set BEFORE the app is imported, so it
  always overrides whatever is in .env for the test process only.
- Three role fixtures (admin/manager/cashier) exist because so much of this
  app's correctness is about *who* is allowed to do *what*.
"""
import os
import sys
import uuid
import tempfile

import pytest

_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"
os.environ["AI_PROVIDER"] = "none"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient  # noqa: E402
from database import sessionLocal, Base, engine  # noqa: E402
from main import app  # noqa: E402
from lifeline.core.security import hash_secret  # noqa: E402
from lifeline.models.user import User, UserRole  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_database():
    """
    Runs before every single test. All tests share one SQLite file (created
    once above, for speed), so without this, data from one test would leak
    into the next — silently breaking any test that asserts on totals
    ("zero sales today", "nothing is low on stock", etc.). Deleting in
    reverse dependency order keeps this safe even without FK enforcement.
    """
    db = sessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()
    yield


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def db_session():
    session = sessionLocal()
    try:
        yield session
    finally:
        session.close()


def _create_user_and_login(client, role, email=None, pin=None):
    email = email or f"{role.lower()}-{uuid.uuid4().hex[:8]}@test.com"
    db = sessionLocal()
    user = User(
        email=email,
        password=hash_secret("password123"),
        pin=hash_secret(pin) if pin else None,
        role=role,
        first_name=role,
        last_name="User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = str(user.user_id)
    db.close()

    resp = client.post("/api/v1/auth/login", data={"username": email, "password": "password123"})
    assert resp.status_code == 200, resp.text
    return {"token": resp.json()["access_token"], "user_id": user_id, "email": email}


@pytest.fixture()
def admin(client):
    return _create_user_and_login(client, UserRole.ADMIN.value, pin="1111")


@pytest.fixture()
def manager(client):
    return _create_user_and_login(client, UserRole.MANAGER.value, pin="2222")


@pytest.fixture()
def cashier(client):
    return _create_user_and_login(client, UserRole.CASHIER.value, pin="3333")


# Back-compat fixture name used by the two original test files.
@pytest.fixture()
def admin_token(admin):
    return admin["token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_headers(admin):
    return auth_headers(admin["token"])


@pytest.fixture()
def manager_headers(manager):
    return auth_headers(manager["token"])


@pytest.fixture()
def cashier_headers(cashier):
    return auth_headers(cashier["token"])


# ---------------------------------------------------------------------------
# Data-creation helpers. Plain functions (not fixtures) so tests can call
# them multiple times with different arguments in the same test.
# ---------------------------------------------------------------------------

def make_product(client, headers, **overrides):
    payload = {
        "product_name": f"Test Product {uuid.uuid4().hex[:6]}",
        "selling_price": 100,
        "current_stock": 50,
        "minimum_stock": 5,
    }
    payload.update(overrides)
    resp = client.post("/api/v1/products/", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def make_customer(client, headers, **overrides):
    payload = {"name": f"Test Customer {uuid.uuid4().hex[:6]}"}
    payload.update(overrides)
    resp = client.post("/api/v1/customers/", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def make_sale(client, headers, items, payments, **overrides):
    payload = {
        "idempotency_key": overrides.pop("idempotency_key", str(uuid.uuid4())),
        "items": items,
        "payments": payments,
    }
    payload.update(overrides)
    return client.post("/api/v1/sales/", json=payload, headers=headers)


@pytest.fixture()
def open_shift(client, admin_headers):
    resp = client.post("/api/v1/shifts/open", json={"opening_cash": 1000}, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()
