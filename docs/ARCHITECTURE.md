# InHouseTX Architecture

## Runtime shape

InHouseTX is a Flask modular monolith. The browser uses a same-origin, dependency-free HTML/CSS/JavaScript interface. Flask serves both the UI and JSON API. SQLite is the default local database; SQLAlchemy accepts PostgreSQL URLs through Psycopg 3. No separate service or frontend build is required.

```text
Browser UI
  ├─ same-origin session API (signed HttpOnly cookie + CSRF token)
  ├─ PayPal JavaScript SDK (public client ID only)
  └─ Flask API
       ├─ identity and ownership checks
       ├─ PayPal Sandbox REST client (OAuth server-side)
       ├─ transaction persistence and audit records
       ├─ TF-IDF + Logistic Regression classifier
       ├─ deterministic analytics and anomaly rules
       └─ grounded deterministic insights (optional OpenAI-compatible wording)
            └─ SQLAlchemy -> SQLite/PostgreSQL

PayPal HTTPS webhook -> signature postback verification -> event-ID dedupe -> state reconciliation
```

## Main modules

- `api/app.py`: application factory, API routes, CSRF, security headers, auth and status handling.
- `api/models.py`: SQLAlchemy user, transaction, PayPal order, webhook event, audit, feedback, budget, anomaly tables.
- `api/paypal.py`: Sandbox OAuth, Orders v2 calls, raw-event-preserving signature verification.
- `api/categorization.py`: TF-IDF/logistic model load/fallback training and linear feature contribution explanations.
- `api/analytics.py`: Decimal-safe, date-filterable and currency-partitioned transaction summaries.
- `api/anomalies.py`: per-user, per-currency historical amount and repeat-frequency signals.
- `api/insights.py`: deterministic answers over analytics facts; optional configured language model receives aggregate facts, never payment tools.
- `frontend/`: served UI for sign-in, spending overview, transactions and details, analytics/filters/budgets, anomaly review, insights, checkout and settings.

## Storage and dates

`users` stores email and Werkzeug password hashes. `transactions` stores user ownership, source, payment status, amounts/currency, PayPal IDs when present, category/confidence/explanation/model ID, and timestamps. `paypal_orders` tracks the server-generated PayPal idempotency keys and capture state. `webhook_events` uses PayPal event ID as the primary key. `payment_audit` records state actions without secrets. Feedback and anomalies are linked to the owning user.

Amounts use `NUMERIC(14,2)`/`Decimal`; summaries never combine currencies. UTC timestamps are stored. For date-only filters, the UI's end date is inclusive; the server converts it to an exclusive next-day bound.

## Schema setup

`python scripts/migrate.py` creates the declarative schema and records schema version 1. The Flask app also initializes the schema at startup so a clean local install works. `Base.metadata.create_all` supports first-run setup but is not an automatic alteration engine; future schema changes must add explicit migration logic before deploying against an existing database.
