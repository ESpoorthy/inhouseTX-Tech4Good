from datetime import datetime, timedelta, timezone
from decimal import Decimal
from api.database import get_db
from api.models import Transaction, Budget
from api.analytics import analytics_summary
from api.anomalies import detect_anomalies
from api.categorization import Categorizer
from tests.conftest import post

def add_tx(db,user,currency,amount,category="Food & Dining",merchant="Cafe",days=0):
    db.add(Transaction(user_id=user,amount=Decimal(amount),currency=currency,description="coffee purchase",merchant=merchant,
        payment_status="COMPLETED",category=category,source="synthetic_demo",created_at=datetime.now(timezone.utc)-timedelta(days=days)))

def test_currency_separation_and_empty(client,signed_in,app):
    assert client.get("/api/analytics/summary").json["currencies"]==[]
    with app.app_context():
        db=get_db();user=db.query(__import__('api.models',fromlist=['User']).User).first()
        add_tx(db,user.id,"USD","12.30");add_tx(db,user.id,"EUR","10.00");db.commit()
        out=analytics_summary(db,user.id,{})
        assert {c["currency"] for c in out["currencies"]}=={"USD","EUR"}
        assert all(c["transaction_count"]==1 for c in out["currencies"])

def test_date_filter(client,signed_in,app):
    with app.app_context():
        db=get_db();u=db.query(__import__('api.models',fromlist=['User']).User).first();add_tx(db,u.id,"USD","5.00",days=3);db.commit()
    assert client.get("/api/analytics/summary?start=not-a-date").status_code==400
    assert client.get("/api/analytics/summary?start=2099-01-01").json["currencies"]==[]

def test_categorizer_returns_real_confidence_and_explanation():
    result=Categorizer().predict("Starbucks coffee purchase")
    assert result["category"] in {"Food & Dining","Fuel","Groceries","Shopping","Transport","Utilities"}
    assert 0 <= result["confidence"] <= 1
    assert result["model_id"] and result["explanation"]["method"]=="linear_tfidf_contributions"

def test_low_confidence_prediction_review(client,signed_in):
    r=post(client,signed_in,"/api/categorization/predict",json={"description":"unfamiliar xyz merchant 9282"})
    assert r.status_code==200 and isinstance(r.json["confidence"],float)
    assert isinstance(r.json["review_required"],bool)

def test_feedback_validates_taxonomy(client,signed_in,app):
    with app.app_context():
        db=get_db();u=db.query(__import__('api.models',fromlist=['User']).User).first();add_tx(db,u.id,"USD","12.30");db.commit();tx=db.query(Transaction).filter_by(user_id=u.id).first();txid=tx.id
    r=post(client,signed_in,f"/api/transactions/{txid}/feedback",json={"corrected_category":"Not a real category"})
    assert r.status_code==400
    r=post(client,signed_in,f"/api/transactions/{txid}/feedback",json={"corrected_category":"Shopping"})
    assert r.status_code==200 and client.get(f"/api/transactions/{txid}").json["transaction"]["category"]=="Shopping"

def test_anomaly_requires_history_and_flags_large_spend(app,client,signed_in):
    with app.app_context():
        db=get_db();u=db.query(__import__('api.models',fromlist=['User']).User).first()
        for days,amt in [(8,"10"),(6,"12"),(4,"11"),(1,"100")]:add_tx(db,u.id,"USD",amt,days=days)
        db.commit();items=detect_anomalies(db,u.id)
        assert len(items)==1 and items[0]["severity"] in {"medium","high"}
        assert "not a fraud" in items[0]["explanation"]

def test_csv_import_is_labeled_and_validated(client,signed_in):
    from io import BytesIO
    data={"file":(BytesIO(b"amount,currency,description,merchant,date\n18.25,USD,Coffee purchase,Corner Cafe,2026-10-20\n"),"activity.csv")}
    r=client.post("/api/transactions/import",data=data,headers={"X-CSRF-Token":signed_in},content_type="multipart/form-data")
    assert r.status_code==201 and r.json["source"]=="csv_import"
    assert r.json["items"][0]["payment_status"]=="IMPORTED"
    assert r.json["items"][0]["source"]=="csv_import"
    bad={"file":(BytesIO(b"amount,currency,description\n10,USD,missing merchant\n"),"bad.csv")}
    assert client.post("/api/transactions/import",data=bad,headers={"X-CSRF-Token":signed_in},content_type="multipart/form-data").status_code==400
