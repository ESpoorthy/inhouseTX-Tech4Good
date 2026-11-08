"""InHouseTX Flask application factory and HTTP API."""
from __future__ import annotations

import os
import secrets
import sys
import time
import csv
import io
from pathlib import Path
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation
from functools import wraps

from flask import Flask, jsonify, request, session, send_from_directory
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.database import configure_database, get_db, init_database, close_db
from api.models import User, Transaction, Feedback, Budget, Anomaly, PayPalOrder, WebhookEvent, AuditLog
from api.analytics import analytics_summary
from api.anomalies import detect_anomalies
from api.categorization import Categorizer
from api.insights import answer_question
from api.paypal import PayPalClient, PayPalError, verify_webhook


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, static_folder="../frontend", static_url_path="/static")
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "local-development-key-change-me"),
        DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///inhouse_tx.db"),
        ENVIRONMENT=os.getenv("ENVIRONMENT", "development"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "false").lower() == "true" or os.getenv("ENVIRONMENT", "development") == "production",
        PAYPAL_CLIENT_ID=os.getenv("PAYPAL_CLIENT_ID", ""),
        PAYPAL_CLIENT_SECRET=os.getenv("PAYPAL_CLIENT_SECRET", ""),
        PAYPAL_WEBHOOK_ID=os.getenv("PAYPAL_WEBHOOK_ID", ""),
        PAYPAL_MODE=os.getenv("PAYPAL_MODE", "sandbox"),
        FRONTEND_ORIGIN=os.getenv("FRONTEND_ORIGIN", ""),
        LOW_CONFIDENCE_THRESHOLD=float(os.getenv("LOW_CONFIDENCE_THRESHOLD", "0.55")),
        AI_PROVIDER=os.getenv("AI_PROVIDER", "deterministic"),
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
        OPENAI_MODEL=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        RATE_LIMIT_PER_MINUTE=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
        MAX_CONTENT_LENGTH=1_000_000,
    )
    if test_config:
        app.config.update(test_config)
    if app.config.get("ENVIRONMENT") == "production" and app.config["SECRET_KEY"] == "local-development-key-change-me":
        raise RuntimeError("Set a unique SECRET_KEY in production.")
    if app.config["PAYPAL_MODE"] != "sandbox":
        raise RuntimeError("This project is Sandbox-only; PAYPAL_MODE must be 'sandbox'.")
    configure_database(app.config["DATABASE_URL"])
    init_database()
    app.teardown_appcontext(close_db)
    app.extensions["categorizer"] = Categorizer(app.config["LOW_CONFIDENCE_THRESHOLD"])
    app.extensions["rate_windows"] = {}
    app.extensions["paypal"] = PayPalClient(
        app.config["PAYPAL_CLIENT_ID"], app.config["PAYPAL_CLIENT_SECRET"]
    )

    # Lightweight same-origin CSRF defense. Cross-origin clients are not enabled by default.
    @app.before_request
    def csrf_guard():
        if request.path.startswith("/api/"):
            now = time.monotonic()
            address = request.remote_addr or "local"
            windows = app.extensions["rate_windows"]
            hits, started = windows.get(address, (0, now))
            if now - started >= 60:
                hits, started = 0, now
            if hits >= app.config["RATE_LIMIT_PER_MINUTE"]:
                return jsonify(error={"code": "rate_limited", "message": "Too many requests. Try again shortly."}), 429
            windows[address] = (hits + 1, started)
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.endpoint not in {
            "auth_signup", "auth_login", "paypal_webhook", "static"
        }:
            if session.get("user_id") and request.headers.get("X-CSRF-Token") != session.get("csrf_token"):
                return jsonify(error={"code": "csrf_failed", "message": "Refresh the page and try again."}), 403
        if app.config["FRONTEND_ORIGIN"] and request.headers.get("Origin"):
            if request.headers["Origin"] != app.config["FRONTEND_ORIGIN"]:
                return jsonify(error={"code": "origin_denied", "message": "Origin is not allowed."}), 403

    def authenticated(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                return jsonify(error={"code": "unauthorized", "message": "Sign in to continue."}), 401
            return fn(*args, **kwargs)
        return wrapped

    def payload():
        return request.get_json(silent=True) if request.is_json else None

    def user_db():
        return get_db().get(User, session["user_id"])

    def error(code, message, status=400):
        return jsonify(error={"code": code, "message": message}), status

    def serialize_tx(tx: Transaction):
        return {
            "id": tx.id, "paypal_order_id": tx.paypal_order_id,
            "paypal_capture_id": tx.paypal_capture_id, "amount": str(tx.amount),
            "currency": tx.currency, "description": tx.description,
            "merchant": tx.merchant, "payment_status": tx.payment_status,
            "payment_timestamp": tx.payment_timestamp.isoformat() if tx.payment_timestamp else None,
            "category": tx.category, "confidence": tx.confidence,
            "explanation": tx.explanation, "model_id": tx.model_id,
            "classified_at": tx.classified_at.isoformat() if tx.classified_at else None,
            "source": tx.source, "created_at": tx.created_at.isoformat(),
            "review_required": tx.review_required,
        }

    def create_transaction(db, user_id: int, amount: Decimal, currency: str, description: str,
                           merchant: str | None, status: str, source: str,
                           order_id: str | None = None, capture_id: str | None = None,
                           happened_at: datetime | None = None):
        result = app.extensions["categorizer"].predict(description or merchant or "")
        tx = Transaction(
            user_id=user_id, amount=amount, currency=currency.upper(), description=(description or "")[:500],
            merchant=(merchant or "")[:160], payment_status=status, source=source,
            paypal_order_id=order_id, paypal_capture_id=capture_id, payment_timestamp=happened_at,
            category=result["category"], confidence=result["confidence"],
            explanation=result["explanation"], model_id=result["model_id"],
            classified_at=datetime.now(timezone.utc),
            review_required=result["confidence"] is not None and result["confidence"] < app.config["LOW_CONFIDENCE_THRESHOLD"],
        )
        db.add(tx)
        db.flush()
        return tx

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", service="inhouse-tx", paypal_mode="sandbox")

    @app.get("/api/ready")
    def ready():
        db = get_db()
        db.execute(select(func.count(User.id))).scalar_one()
        return jsonify(status="ready", database="ok", paypal_configured=app.extensions["paypal"].configured)

    @app.post("/api/auth/signup")
    def auth_signup():
        data = payload()
        if not isinstance(data, dict):
            return error("invalid_json", "Send a JSON object.")
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        if len(email) > 254 or "@" not in email or len(password) < 10 or len(password) > 200:
            return error("invalid_credentials", "Use a valid email and a password of at least 10 characters.")
        db = get_db()
        user = User(email=email, password_hash=generate_password_hash(password))
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return error("account_exists", "An account already exists for this email.", 409)
        session.clear()
        session["user_id"] = user.id
        session["csrf_token"] = secrets.token_urlsafe(32)
        return jsonify(user={"id": user.id, "email": user.email}, csrf_token=session["csrf_token"]), 201

    @app.post("/api/auth/login")
    def auth_login():
        data = payload()
        if not isinstance(data, dict):
            return error("invalid_json", "Send a JSON object.")
        email = str(data.get("email", "")).strip().lower()
        user = get_db().scalar(select(User).where(User.email == email))
        if not user or not check_password_hash(user.password_hash, str(data.get("password", ""))):
            return error("invalid_credentials", "Email or password is incorrect.", 401)
        session.clear()
        session["user_id"] = user.id
        session["csrf_token"] = secrets.token_urlsafe(32)
        return jsonify(user={"id": user.id, "email": user.email}, csrf_token=session["csrf_token"])

    @app.post("/api/auth/logout")
    @authenticated
    def auth_logout():
        session.clear()
        return jsonify(status="signed_out")

    @app.get("/api/auth/session")
    def auth_session():
        user_id = session.get("user_id")
        if not user_id:
            return jsonify(authenticated=False)
        user = get_db().get(User, user_id)
        if not user:
            session.clear()
            return jsonify(authenticated=False)
        if not session.get("csrf_token"):
            session["csrf_token"] = secrets.token_urlsafe(32)
        return jsonify(authenticated=True, user={"id": user.id, "email": user.email}, csrf_token=session["csrf_token"])

    @app.get("/api/settings/integrations")
    @authenticated
    def integration_status():
        pp = app.extensions["paypal"]
        return jsonify(paypal={"mode": "sandbox", "configured": pp.configured,
                               "client_id": pp.client_id if pp.configured else None,
                               "checkout_available": pp.configured,
                               "webhook_verification_available": bool(app.config["PAYPAL_WEBHOOK_ID"]),
                               "message": "Sandbox credentials are configured." if pp.configured else "Add Sandbox credentials to enable live Sandbox checkout."},
                       insights={"provider": app.config["AI_PROVIDER"], "mode": "llm" if app.config["AI_PROVIDER"] == "openai" and app.config["OPENAI_API_KEY"] else "deterministic"})

    @app.post("/api/categorization/predict")
    @authenticated
    def categorization_predict():
        data = payload()
        if not isinstance(data, dict) or not isinstance(data.get("description"), str) or not data["description"].strip():
            return error("invalid_transaction", "A non-empty description is required.")
        result = app.extensions["categorizer"].predict(data["description"][:500])
        return jsonify(**result)

    @app.post("/api/paypal/orders")
    @authenticated
    def paypal_create_order():
        data = payload()
        if not isinstance(data, dict):
            return error("invalid_json", "Send a JSON object.")
        try:
            amount = Decimal(str(data.get("amount", ""))).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return error("invalid_amount", "Amount must be a valid decimal value.")
        currency = str(data.get("currency", "USD")).upper()
        description = str(data.get("description", "PayPal Sandbox demo payment")).strip()
        if amount <= 0 or amount > Decimal("10000.00") or currency != "USD":
            return error("invalid_payment", "Sandbox demo checkout accepts amounts above zero up to 10,000 USD.")
        if not description or len(description) > 120:
            return error("invalid_description", "Description must be between 1 and 120 characters.")
        pp: PayPalClient = app.extensions["paypal"]
        if not pp.configured:
            return error("paypal_not_configured", "Configure PayPal Sandbox client credentials first.", 503)
        request_key = request.headers.get("Idempotency-Key") or request.headers.get("PayPal-Request-Id") or secrets.token_hex(16)
        if len(request_key) > 38 or len(request_key) < 8:
            return error("invalid_idempotency_key", "Idempotency key must be 8 to 38 characters.")
        existing = get_db().scalar(select(PayPalOrder).where(PayPalOrder.user_id == session["user_id"],
                                                              PayPalOrder.request_id == request_key))
        if existing:
            return jsonify(order_id=existing.order_id, status=existing.status, approve_url=None,
                           mode="sandbox", idempotent_replay=True), 200
        try:
            created = pp.create_order(amount, currency, description, request_key)
        except PayPalError as exc:
            return error("paypal_error", exc.public_message, 502)
        db = get_db()
        order = PayPalOrder(user_id=session["user_id"], order_id=created["id"], amount=amount,
                            currency=currency, description=description, status=created.get("status", "CREATED"),
                            request_id=request_key, capture_request_id=secrets.token_urlsafe(24))
        db.add(order)
        db.add(AuditLog(user_id=session["user_id"], action="paypal_order_created", external_id=order.order_id))
        db.commit()
        return jsonify(order_id=order.order_id, status=order.status,
                       approve_url=created.get("approve_url"), mode="sandbox"), 201

    @app.get("/api/paypal/orders/<order_id>")
    @authenticated
    def paypal_get_order(order_id):
        db = get_db()
        order = db.scalar(select(PayPalOrder).where(PayPalOrder.order_id == order_id,
                                                     PayPalOrder.user_id == session["user_id"]))
        if not order:
            return error("order_not_found", "Order not found.", 404)
        pp: PayPalClient = app.extensions["paypal"]
        if pp.configured:
            try:
                remote = pp.get_order(order_id)
                if not order.capture_id and order.status == "CREATED":
                    order.status = remote.get("status", order.status)
                    db.commit()
            except PayPalError as exc:
                return error("paypal_error", exc.public_message, 502)
        return jsonify(order_id=order.order_id, status=order.status, amount=str(order.amount),
                       currency=order.currency, mode="sandbox")

    @app.post("/api/paypal/orders/<order_id>/capture")
    @authenticated
    def paypal_capture_order(order_id):
        db = get_db()
        order = db.scalar(select(PayPalOrder).where(PayPalOrder.order_id == order_id,
                                                     PayPalOrder.user_id == session["user_id"]))
        if not order:
            return error("order_not_found", "Order not found.", 404)
        if order.capture_id:
            tx = db.scalar(select(Transaction).where(Transaction.paypal_capture_id == order.capture_id))
            code = 200 if order.status == "COMPLETED" else 202
            return jsonify(status=order.status, transaction=serialize_tx(tx) if tx else None, idempotent_replay=True), code
        if not app.extensions["paypal"].configured:
            return error("paypal_not_configured", "Configure PayPal Sandbox credentials first.", 503)
        try:
            captured = app.extensions["paypal"].capture_order(order_id, order.capture_request_id)
        except PayPalError as exc:
            return error("paypal_error", exc.public_message, 502)
        capture_status = str(captured.get("status", "PENDING")).upper()
        if capture_status == "COMPLETED" and not captured.get("capture_id"):
            capture_status = "PENDING"
        order.status = capture_status
        amount, currency, capture_id = captured.get("amount"), captured.get("currency"), captured.get("capture_id")
        tx = None
        if capture_id and amount is not None and currency:
            if amount != order.amount or currency != order.currency:
                order.capture_id = capture_id
                order.captured_at = captured["captured_at"]
                db.add(AuditLog(user_id=order.user_id, action="paypal_capture_amount_mismatch",
                                external_id=capture_id, details=f"expected {order.amount} {order.currency}; received {amount} {currency}"))
                db.commit()
                return error("capture_mismatch", "Captured amount or currency did not match the approved order.", 409)
            order.capture_id = capture_id
            order.captured_at = captured["captured_at"]
            tx = create_transaction(db, order.user_id, amount, currency, order.description,
                                    captured.get("merchant") or "PayPal Sandbox", capture_status, "paypal_sandbox",
                                    order.order_id, capture_id, captured["captured_at"])
        db.add(AuditLog(user_id=order.user_id, action=f"paypal_capture_{capture_status.lower()}",
                        external_id=capture_id or order.order_id))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            tx = db.scalar(select(Transaction).where(Transaction.paypal_capture_id == capture_id))
        if capture_status != "COMPLETED":
            return jsonify(status=capture_status, transaction=serialize_tx(tx) if tx else None,
                           message="PayPal has not confirmed a completed capture."), 202
        return jsonify(status="COMPLETED", transaction=serialize_tx(tx), idempotent_replay=False)

    @app.post("/api/paypal/webhooks")
    def paypal_webhook():
        raw = request.get_data(cache=True)
        event = request.get_json(silent=True)
        if not isinstance(event, dict) or not event.get("id"):
            return error("invalid_event", "Webhook event body is invalid.")
        if not verify_webhook(raw, event, request.headers, app.config["PAYPAL_WEBHOOK_ID"], app.extensions["paypal"]):
            return error("invalid_webhook_signature", "PayPal webhook signature could not be verified.", 401)
        db = get_db()
        existing = db.get(WebhookEvent, event["id"])
        if existing:
            return jsonify(status="already_processed" if existing.processed else "already_received"), 200
        record = WebhookEvent(event_id=event["id"], event_type=event.get("event_type", "unknown"), processed=False)
        db.add(record)
        try:
            db.flush()
            event_status = {"PAYMENT.CAPTURE.COMPLETED": "COMPLETED",
                            "PAYMENT.CAPTURE.PENDING": "PENDING",
                            "PAYMENT.CAPTURE.DENIED": "DENIED"}.get(event.get("event_type"))
            if event_status:
                resource = event.get("resource", {})
                order_id = resource.get("supplementary_data", {}).get("related_ids", {}).get("order_id")
                cap_id = resource.get("id")
                order = db.scalar(select(PayPalOrder).where(PayPalOrder.order_id == order_id)) if order_id else None
                if order and cap_id:
                    try:
                        amt = Decimal(resource["amount"]["value"])
                        curr = resource["amount"]["currency_code"]
                    except (KeyError, InvalidOperation, TypeError):
                        amt, curr = None, None
                    if amt == order.amount and curr == order.currency and (not order.capture_id or order.capture_id == cap_id):
                        order.status, order.capture_id = event_status, cap_id
                        if resource.get("update_time"):
                            try:
                                order.captured_at = datetime.fromisoformat(resource["update_time"].replace("Z", "+00:00"))
                            except ValueError:
                                pass
                        tx = db.scalar(select(Transaction).where(Transaction.paypal_capture_id == cap_id))
                        if tx:
                            tx.payment_status = event_status
                            tx.payment_timestamp = order.captured_at or tx.payment_timestamp
                        else:
                            tx = create_transaction(db, order.user_id, amt, curr, order.description,
                                "PayPal Sandbox", event_status, "paypal_sandbox", order.order_id, cap_id,
                                order.captured_at or datetime.now(timezone.utc))
                        db.add(AuditLog(user_id=order.user_id, action=f"paypal_webhook_capture_{event_status.lower()}", external_id=cap_id))
                    else:
                        db.add(AuditLog(user_id=order.user_id, action="paypal_webhook_capture_mismatch",
                                        external_id=cap_id, details="Webhook order, capture, amount or currency mismatch"))
            record.processed = True
            db.commit()
        except IntegrityError:
            db.rollback()  # concurrent duplicate event; the first transaction owns the event ID
        return jsonify(status="received"), 200

    @app.get("/api/transactions")
    @authenticated
    def transactions_list():
        db = get_db()
        stmt = select(Transaction).where(Transaction.user_id == session["user_id"])
        for key, column in (("category", Transaction.category), ("currency", Transaction.currency),
                            ("status", Transaction.payment_status), ("source", Transaction.source),
                            ("merchant", Transaction.merchant)):
            val = request.args.get(key)
            if val:
                stmt = stmt.where(column.ilike(f"%{val[:100]}%") if key == "merchant" else column == val)
        start = request.args.get("start")
        end = request.args.get("end")
        try:
            def parse_bound(value):
                parsed = datetime.fromisoformat(value)
                return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed
            if start:
                stmt = stmt.where(func.coalesce(Transaction.payment_timestamp, Transaction.created_at) >= parse_bound(start))
            if end:
                end_bound = parse_bound(end)
                if len(end) == 10:
                    end_bound += timedelta(days=1)
                stmt = stmt.where(func.coalesce(Transaction.payment_timestamp, Transaction.created_at) < end_bound)
        except ValueError:
            return error("invalid_date", "Dates must use ISO 8601 format.")
        limit = min(max(request.args.get("limit", 50, type=int), 1), 100)
        offset = max(request.args.get("offset", 0, type=int), 0)
        total = db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = db.scalars(stmt.order_by(Transaction.created_at.desc()).limit(limit).offset(offset)).all()
        return jsonify(items=[serialize_tx(x) for x in rows], total=total, limit=limit, offset=offset)

    @app.get("/api/transactions/<int:tx_id>")
    @authenticated
    def transaction_detail(tx_id):
        tx = get_db().scalar(select(Transaction).where(Transaction.id == tx_id,
                                                       Transaction.user_id == session["user_id"]))
        return (jsonify(transaction=serialize_tx(tx)), 200) if tx else error("not_found", "Transaction not found.", 404)

    @app.post("/api/transactions/import")
    @authenticated
    def transactions_import():
        uploaded = request.files.get("file")
        if not uploaded or not uploaded.filename or not uploaded.filename.lower().endswith(".csv"):
            return error("invalid_file", "Upload a CSV file.")
        raw = uploaded.stream.read(1_000_001)
        if len(raw) > 1_000_000:
            return error("file_too_large", "CSV files must be smaller than 1 MB.", 413)
        try:
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
            required = {"amount", "currency", "description", "merchant"}
            if not required.issubset(set(reader.fieldnames or [])):
                return error("invalid_columns", "CSV must include amount,currency,description,merchant columns.")
            rows = list(reader)
        except (UnicodeDecodeError, csv.Error):
            return error("invalid_csv", "CSV must be valid UTF-8 with a header row.")
        if not rows or len(rows) > 100:
            return error("invalid_row_count", "Include between 1 and 100 transaction rows.")
        db = get_db()
        created = []
        try:
            for line, row in enumerate(rows, start=2):
                amount = Decimal(str(row.get("amount", "")).strip()).quantize(Decimal("0.01"))
                currency = str(row.get("currency", "")).strip().upper()
                description = str(row.get("description", "")).strip()
                merchant = str(row.get("merchant", "")).strip()
                if amount <= 0 or amount > Decimal("100000000") or len(currency) != 3 or not currency.isalpha():
                    raise ValueError(f"Row {line}: amount or currency is invalid.")
                if not description or len(description) > 500 or len(merchant) > 160:
                    raise ValueError(f"Row {line}: description or merchant is invalid.")
                happened = None
                if row.get("date", "").strip():
                    happened = datetime.fromisoformat(row["date"].strip())
                    if happened.tzinfo is None:
                        happened = happened.replace(tzinfo=timezone.utc)
                result = app.extensions["categorizer"].predict(description)
                tx = Transaction(user_id=session["user_id"], amount=amount, currency=currency,
                    description=description, merchant=merchant, payment_status="IMPORTED", source="csv_import",
                    payment_timestamp=happened, category=result["category"], confidence=result["confidence"],
                    explanation=result["explanation"], model_id=result["model_id"],
                    classified_at=datetime.now(timezone.utc), review_required=result["review_required"])
                db.add(tx)
                db.flush()
                created.append(tx)
            db.commit()
        except (ValueError, InvalidOperation, KeyError) as exc:
            db.rollback()
            return error("invalid_csv_row", str(exc))
        return jsonify(imported=len(created), items=[serialize_tx(tx) for tx in created],
                       source="csv_import", note="Imported records are not PayPal-verified payments."), 201

    @app.post("/api/transactions/<int:tx_id>/feedback")
    @authenticated
    def transaction_feedback(tx_id):
        data = payload()
        if not isinstance(data, dict) or not data.get("corrected_category"):
            return error("invalid_feedback", "A corrected_category is required.")
        category = str(data["corrected_category"])[:80]
        db = get_db()
        tx = db.scalar(select(Transaction).where(Transaction.id == tx_id,
                                                  Transaction.user_id == session["user_id"]))
        if not tx:
            return error("not_found", "Transaction not found.", 404)
        if category not in app.extensions["categorizer"].categories:
            return error("invalid_category", "Choose a category from the configured taxonomy.")
        db.add(Feedback(transaction_id=tx.id, user_id=tx.user_id, original_category=tx.category,
                        corrected_category=category, original_confidence=tx.confidence,
                        model_id=tx.model_id, comment=str(data.get("comment", ""))[:500]))
        tx.category = category
        tx.review_required = False
        db.commit()
        return jsonify(status="saved", category=category)

    @app.get("/api/analytics/summary")
    @authenticated
    def analytics():
        try:
            return jsonify(analytics_summary(get_db(), session["user_id"], request.args))
        except ValueError as exc:
            return error("invalid_filter", str(exc))

    @app.get("/api/anomalies")
    @authenticated
    def anomalies():
        db = get_db()
        results = detect_anomalies(db, session["user_id"])
        return jsonify(items=results)

    @app.post("/api/anomalies/<int:anomaly_id>/review")
    @authenticated
    def anomaly_review(anomaly_id):
        data = payload()
        status = data.get("status") if isinstance(data, dict) else None
        if status not in {"reviewed", "dismissed"}:
            return error("invalid_status", "Status must be reviewed or dismissed.")
        anomaly = get_db().scalar(select(Anomaly).where(Anomaly.id == anomaly_id,
                                                        Anomaly.user_id == session["user_id"]))
        if not anomaly:
            return error("not_found", "Anomaly not found.", 404)
        anomaly.review_status = status
        get_db().commit()
        return jsonify(status=status)

    @app.get("/api/budgets")
    @authenticated
    def budgets_list():
        rows = get_db().scalars(select(Budget).where(Budget.user_id == session["user_id"]).order_by(Budget.category)).all()
        return jsonify(items=[{"id": b.id, "category": b.category, "currency": b.currency,
                               "amount": str(b.amount), "period": b.period} for b in rows])

    @app.post("/api/budgets")
    @authenticated
    def budget_create():
        data = payload()
        try:
            amount = Decimal(str(data.get("amount", ""))).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError, AttributeError):
            return error("invalid_amount", "Enter a valid budget amount.")
        category, currency = str(data.get("category", "")), str(data.get("currency", "USD")).upper()
        if category not in app.extensions["categorizer"].categories or amount <= 0 or len(currency) != 3:
            return error("invalid_budget", "Choose a valid category, positive amount, and three-letter currency.")
        budget = Budget(user_id=session["user_id"], category=category, currency=currency,
                        amount=amount, period="monthly")
        db = get_db()
        old = db.scalar(select(Budget).where(Budget.user_id == budget.user_id,
                                             Budget.category == category, Budget.currency == currency))
        if old:
            old.amount = amount
        else:
            db.add(budget)
        db.commit()
        return jsonify(status="saved"), 201

    @app.post("/api/insights/query")
    @authenticated
    def insights_query():
        data = payload()
        question = str(data.get("question", "")).strip() if isinstance(data, dict) else ""
        if not question or len(question) > 1000:
            return error("invalid_question", "Enter a question up to 1,000 characters.")
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if "last month" in question.lower():
            end = month_start
            start = (month_start - timedelta(days=1)).replace(day=1)
            period = {"start": start.date().isoformat(), "end": (end - timedelta(days=1)).date().isoformat()}
        elif "this month" in question.lower():
            start = month_start
            period = {"start": start.date().isoformat(), "end": now.date().isoformat()}
        elif "last 30 days" in question.lower() or "past 30 days" in question.lower():
            start = now - timedelta(days=29)
            period = {"start": start.date().isoformat(), "end": now.date().isoformat()}
        else:
            period = {}
        facts = analytics_summary(get_db(), session["user_id"], period)
        response = answer_question(question, facts, app.config)
        return jsonify(**response)

    @app.errorhandler(429)
    def too_many_requests(_):
        return error("rate_limited", "Too many requests. Try again shortly.", 429)

    @app.errorhandler(500)
    def internal_error(_):
        get_db().rollback()
        app.logger.exception("Unhandled server error")
        return error("internal_error", "The request could not be completed.", 500)

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' https://www.paypal.com https://www.sandbox.paypal.com; frame-src https://www.paypal.com https://www.sandbox.paypal.com; connect-src 'self' https://api-m.sandbox.paypal.com https://www.paypal.com https://www.sandbox.paypal.com; style-src 'self' 'unsafe-inline'; img-src 'self' data:"
        return response

    @app.get("/")
    def frontend_index():
        if os.path.isfile(os.path.join(app.static_folder or "", "index.html")):
            return send_from_directory(app.static_folder, "index.html")
        return jsonify(service="InHouseTX API", frontend="Build frontend with npm run build in frontend/"), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
