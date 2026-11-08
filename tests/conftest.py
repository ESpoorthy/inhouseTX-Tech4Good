import pytest
from api.app import create_app

@pytest.fixture
def app():
    return create_app({"TESTING": True, "SECRET_KEY": "pytest-secret-key", "DATABASE_URL": "sqlite:///:memory:",
                       "PAYPAL_CLIENT_ID": "sandbox-client", "PAYPAL_CLIENT_SECRET": "sandbox-secret",
                       "PAYPAL_WEBHOOK_ID": "webhook-test-id", "RATE_LIMIT_PER_MINUTE": 300})

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def signed_in(client):
    r = client.post("/api/auth/signup", json={"email": "person@example.test", "password": "a-strong-test-password"})
    assert r.status_code == 201
    return r.json["csrf_token"]

def post(client, token, path, **kwargs):
    return client.post(path, headers={"X-CSRF-Token": token}, **kwargs)
