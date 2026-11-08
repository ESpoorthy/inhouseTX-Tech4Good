"""Create an isolated account and synthetic transactions for local demo use."""
from __future__ import annotations
import argparse
import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from werkzeug.security import generate_password_hash
from sqlalchemy import select
from api.app import create_app
from api.database import get_db
from api.models import User, Transaction, Anomaly, Feedback

parser = argparse.ArgumentParser()
parser.add_argument("--email", default="demo@inhouse-tx.local")
args = parser.parse_args()
app = create_app()
password = secrets.token_urlsafe(14)
fixtures = [
    ("Coffee shop purchase", "Blue Bottle Cafe", "Food & Dining", "100.00", 0),
    ("Grocery market receipt", "Trader Joes Grocery", "Groceries", "42.15", 1),
    ("Ride payment", "Uber Trip", "Transport", "18.40", 2),
    ("Online marketplace order", "Amazon Marketplace", "Shopping", "29.99", 3),
    ("Fuel station payment", "Shell Fuel", "Fuel", "48.70", 4),
    ("Monthly internet bill", "Internet Service Bill", "Utilities", "65.00", 5),
    ("Restaurant payment", "Chipotle Mexican Grill", "Food & Dining", "13.25", 6),
    ("Supermarket purchase", "Whole Foods Market", "Groceries", "38.60", 8),
    ("Late-night repeated order", "Online Marketplace", "Shopping", "245.00", 9),
    ("Cafe payment", "Starbucks Coffee", "Food & Dining", "7.20", 10),
    ("Metro pass reload", "Metro Transit Pass", "Transport", "24.00", 12),
    ("Phone service monthly", "Mobile Phone Bill", "Utilities", "42.00", 14),
    ("Cafe visit", "Neighborhood Coffee", "Food & Dining", "10.00", 60),
    ("Coffee payment", "Neighborhood Coffee", "Food & Dining", "11.00", 30),
]
with app.app_context():
    db = get_db()
    user = db.scalar(select(User).where(User.email == args.email.lower()))
    if user:
        user.password_hash = generate_password_hash(password)
        old_ids = [row[0] for row in db.query(Transaction.id).filter(Transaction.user_id == user.id, Transaction.source == "synthetic_demo").all()]
        if old_ids:
            db.query(Anomaly).filter(Anomaly.transaction_id.in_(old_ids)).delete(synchronize_session=False)
            db.query(Feedback).filter(Feedback.transaction_id.in_(old_ids)).delete(synchronize_session=False)
            db.query(Transaction).filter(Transaction.id.in_(old_ids)).delete(synchronize_session=False)
    else:
        user = User(email=args.email.lower(), password_hash=generate_password_hash(password))
        db.add(user)
        db.flush()
    now = datetime.now(timezone.utc)
    cat = app.extensions["categorizer"]
    for description, merchant, expected, amount, days in fixtures:
        result = cat.predict(description + " " + merchant)
        tx = Transaction(user_id=user.id, amount=Decimal(amount), currency="USD", description=description,
            merchant=merchant, payment_status="COMPLETED", payment_timestamp=now-timedelta(days=days),
            category=result["category"], confidence=result["confidence"], explanation=result["explanation"],
            model_id=result["model_id"], classified_at=now-timedelta(days=days), review_required=False,
            source="synthetic_demo", created_at=now-timedelta(days=days))
        db.add(tx)
    db.commit()
    print(f"Demo account: {args.email.lower()}")
    print(f"One-time password: {password if user.id else '(stored)'}")
    print(f"{len(fixtures)} transactions created as synthetic_demo; no PayPal payment was made.")
