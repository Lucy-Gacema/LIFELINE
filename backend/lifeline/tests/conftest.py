import os
import sys
import tempfile

import pytest


_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"
os.environ["AI_PROVIDER"] = "none"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient  
from database import sessionLocal  
from main import app 


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


@pytest.fixture()
def admin_token(client):
    from lifeline.core.security import hash_secret
    from lifeline.models.user import User, UserRole
    db = sessionLocal()
    user = User(
        email="admin@test.com", password=hash_secret("password123"),
        role=UserRole.ADMIN.value, first_name="Admin", last_name="User",
    )
    db.add(user)
    db.commit()
    db.close()

    resp = client.post("/api/v1/auth/login", data={"username": "admin@test.com", "password": "password123"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]
