from api.database import get_db
from api.models import User, Transaction
from decimal import Decimal
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from tests.conftest import post

def test_health_readiness_and_frontend(client):
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/ready").json["status"] == "ready"
    assert client.get("/").status_code == 200
    assert client.get("/static/vanilla.js").status_code == 200

def test_auth_required_and_csrf(client, signed_in):
    assert client.get("/api/transactions").status_code == 200
    assert client.post("/api/auth/logout", json={}).status_code == 403
    assert client.post("/api/auth/logout", json={}, headers={"X-CSRF-Token": signed_in}).status_code == 200
    assert client.get("/api/transactions").status_code == 401

def test_signup_validation_and_login(client):
    assert client.post("/api/auth/signup", json={"email":"x", "password":"short"}).status_code == 400
    r = client.post("/api/auth/signup", json={"email":"one@example.test", "password":"long-enough-test-pass"})
    assert r.status_code == 201
    assert client.post("/api/auth/signup", json={"email":"one@example.test", "password":"long-enough-test-pass"}).status_code == 409
    client.post("/api/auth/logout", json={}, headers={"X-CSRF-Token":r.json["csrf_token"]})
    assert client.post("/api/auth/login", json={"email":"one@example.test", "password":"wrong-password"}).status_code == 401
    assert client.post("/api/auth/login", json={"email":"one@example.test", "password":"long-enough-test-pass"}).status_code == 200

def test_user_isolation(app, client, signed_in):
    with app.app_context():
        db=get_db(); other=User(email="other@example.test",password_hash=generate_password_hash("a-strong-test-password"));db.add(other);db.flush()
        db.add(Transaction(user_id=other.id,amount=Decimal("15.00"),currency="USD",description="private",merchant="Private Shop",payment_status="COMPLETED",category="Shopping",source="synthetic_demo",created_at=datetime.now(timezone.utc)))
        db.commit(); txid=db.query(Transaction).filter_by(user_id=other.id).first().id
    assert client.get("/api/transactions").json["total"] == 0
    assert client.get(f"/api/transactions/{txid}").status_code == 404

def test_rate_limit(client):
    from api.app import create_app
    app=create_app({"TESTING":True,"SECRET_KEY":"x","DATABASE_URL":"sqlite:///:memory:","RATE_LIMIT_PER_MINUTE":1})
    c=app.test_client()
    assert c.get("/api/health").status_code == 200
    assert c.get("/api/health").status_code == 429
