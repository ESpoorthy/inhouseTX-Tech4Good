# Design — InHouseTX PayPal AI Spending Intelligence

**Status:** Approved and implemented design baseline; see tasks.md and final reports for implementation state and external verification gaps.

## Architecture

Start as a modular monolith on Flask to preserve the existing app. Suggested modules: `api`, `security`, `database`, `transactions`, `paypal`, `categorisation`, `analytics`, `anomalies`, `insights`, and `frontend`. Keep PayPal and optional LLM integrations behind service interfaces. Existing ML files remain the initial inference implementation; refactor paths/configuration and artifact metadata only after tests characterize behavior.

```text
Responsive browser UI
  -> Flask API (authentication, validation, authorization)
    -> services: PayPal | transactions | categorisation | analytics | anomalies | insights
      -> relational database; local model artifacts; PayPal Sandbox REST API
      -> optional LLM for wording only, with analytics facts as constrained input
PayPal webhook -> signature verification -> event deduplication -> transaction state reconciliation
```

## Components

- **API:** versioned JSON routes, request schemas, stable errors, health/readiness status.
- **Identity/security:** authenticated principal resolved server side; ownership filters applied in query/service layer; no user ID trusted from client payload.
- **Database:** relational persistence (SQLite acceptable for local demo; deployment DB choice after platform decision), migrations, uniqueness constraints on PayPal order/capture and webhook event IDs.
- **PayPal service:** Sandbox base URL, OAuth token handling, create/get/capture order, webhook verification, timeout/retry policy, idempotency key, redacted audit events.
- **Transaction service:** normalizes verified provider events or labeled fixtures into one model; avoids duplicate imports and keeps provider status authoritative.
- **Categorisation service:** calls existing TF-IDF + LightGBM pipeline; records model/version and probability-derived confidence; wraps SHAP only after output shape is verified; low-confidence review state.
- **Analytics service:** SQL/Python deterministic grouping with Decimal amounts and currency partitioning.
- **Anomaly service:** per-user, per-currency statistical baselines; explain score and comparison; insufficient history yields “not enough history,” not a fabricated score.
- **Insights service:** tool/data access limited to authorized analytics results; deterministic totals; optional language model cannot execute payment actions.
- **Frontend:** responsive dashboard and checkout approval integration; no PayPal secret or authoritative payment state in client.

## Database schema (initial proposal)

- `users(id, email_or_subject, password_hash_or_identity_subject, created_at)` — choose auth mechanism before implementation; never store plaintext passwords.
- `transactions(id, user_id FK, paypal_order_id nullable UNIQUE, paypal_capture_id nullable UNIQUE, amount DECIMAL, currency CHAR(3), description, merchant, payment_status, payment_timestamp, source ENUM, category, confidence DECIMAL nullable, explanation JSON nullable, model_id nullable, classified_at nullable, created_at, updated_at)`.
- `paypal_webhook_events(event_id PK, event_type, resource_id, received_at, verification_status, processed_at, processing_status)` — restrict payload retention; raw event body need not be persisted.
- `payment_audit(id, user_id, order_id, capture_id, action, prior_status, new_status, occurred_at, correlation_id)` — no secrets or unnecessary payment instrument data.
- `classification_feedback(id, transaction_id FK, user_id FK, original_category, corrected_category, original_confidence, user_feedback, model_id, created_at, review_status)`.
- `budgets(id, user_id FK, category, currency, amount DECIMAL, period, starts_on, ends_on)`.
- `anomalies(id, transaction_id FK, score, severity, explanation, baseline JSON, created_at, review_status)`.

Use database constraints, indexes for user/date/currency/category and unique external IDs, migration tooling, and transactional updates. Store timestamps in UTC and serialize with timezone offsets.

## API outline

- `POST /api/paypal/orders` — authenticated; validate amount/currency and create Sandbox order.
- `POST /api/paypal/orders/{order_id}/capture` — authenticated owner-bound order capture; idempotent.
- `GET /api/paypal/orders/{order_id}` — owner-bound status fetched/reconciled server side.
- `POST /api/paypal/webhooks` — provider-authenticated, event-ID idempotent; no user session requirement.
- `GET /api/transactions` — scoped filters: date range, category, merchant, currency, status.
- `GET /api/transactions/{id}` — owner-bound details.
- `POST /api/transactions/{id}/feedback` — corrected category and optional feedback.
- `POST /api/transactions/import` — optional CSV, strict schema/size/row validation, source labeled imported.
- `GET /api/analytics/summary`, `/categories`, `/trends`, `/merchants`, `/budgets` — deterministic scoped outputs, grouped by currency.
- `GET /api/anomalies` — scoped explainable flags.
- `POST /api/insights/query` — validated natural-language question; answer cites period/currency and grounded result references.
- `GET /health` and `GET /ready` — liveness vs dependency readiness without leaking details.

Exact route schemas/status codes will be fixed during implementation after official PayPal API verification.

## PayPal integration sequence

1. Backend obtains OAuth access token from Sandbox credentials.
2. Backend creates an order with server-validated amount/currency and a stable idempotency key.
3. UI uses the supported approval experience and receives provider approval; this alone is not payment success.
4. Backend captures the specific order through PayPal and validates the response/status and capture details.
5. Persist a transaction only from verified server-side provider state, idempotently.
6. Webhook endpoint verifies authenticity through the current official supported method, deduplicates event ID, reconciles authoritative state, and records audit transition.
7. Conflicts/out-of-order events trigger provider re-fetch/reconciliation; do not regress a completed capture.

Sandbox-only environment guard, secret redaction, timeouts and bounded retries are mandatory. Current official request/response and verification formats must be rechecked before coding.

## AI processing pipeline

Verified/imported/demo-labeled transaction -> schema validation -> persistence with provenance -> category inference -> review threshold -> deterministic analytics/anomaly baselines -> grounded insight facts -> optional natural-language rendering. Transaction descriptions are data only and never instructions. No LLM computes money or changes payment state.

## Deployment and operations

Target a single backend service plus static frontend and relational DB for hackathon simplicity. Container/migration/health-check specifics depend on host selection. Environment supplies Sandbox client ID/secret, webhook ID, database URL, auth secret, allowed origins, and optional LLM key; `.env.example` lists names with placeholders only. Never commit credentials or generated user data.
