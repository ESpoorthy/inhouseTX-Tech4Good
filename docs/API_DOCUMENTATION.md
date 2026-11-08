# API Reference

All `/api` routes use JSON unless a CSV import is noted. Most routes require an authenticated session. JSON mutation requests must include `X-CSRF-Token` returned from `/api/auth/signup`, `/api/auth/login`, or `/api/auth/session`. Error shape: `{ "error": { "code": "...", "message": "..." } }`.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/health`, `/api/ready` | No | Liveness and dependency readiness |
| POST | `/api/auth/signup`, `/api/auth/login` | No | Create account/sign in; returns user and CSRF token |
| POST | `/api/auth/logout` | Yes + CSRF | Clear session |
| GET | `/api/auth/session` | Optional | Current session and CSRF token |
| GET | `/api/settings/integrations` | Yes | Sandbox and insights provider status; public client ID only |
| POST | `/api/paypal/orders` | Yes + CSRF | Server creates Sandbox order; accepts amount/currency/description and optional `Idempotency-Key` |
| GET | `/api/paypal/orders/{id}` | Yes | Owner-scoped provider status lookup |
| POST | `/api/paypal/orders/{id}/capture` | Yes + CSRF | Server capture and payment reconciliation |
| POST | `/api/paypal/webhooks` | Provider signature | Verify/dedupe/reconcile a PayPal event |
| GET | `/api/transactions` | Yes | Filters: start/end/category/merchant/currency/status/source; limit 1–100, offset |
| GET | `/api/transactions/{id}` | Yes | Owner-scoped detail and explanation |
| POST | `/api/transactions/{id}/feedback` | Yes + CSRF | Persist valid taxonomy correction |
| POST | `/api/transactions/import` | Yes + CSRF | Multipart CSV upload, up to 1 MB and 100 rows |
| POST | `/api/categorization/predict` | Yes + CSRF | Predict from a description; returns category/confidence/features/model ID/review flag |
| GET | `/api/analytics/summary` | Yes | Currency-partitioned deterministic summaries and filters |
| GET | `/api/anomalies` | Yes | Explainable anomaly signals |
| POST | `/api/anomalies/{id}/review` | Yes + CSRF | Mark reviewed or dismissed |
| GET/POST | `/api/budgets` | Yes / Yes + CSRF | List and save monthly category budget |
| POST | `/api/insights/query` | Yes + CSRF | Grounded deterministic response for a question |

## CSV schema

```csv
amount,currency,description,merchant,date
18.50,USD,Coffee shop purchase,Corner Cafe,2026-11-02
```

Imported source and status remain `csv_import` and `IMPORTED`; they are not PayPal events. Category is predicted by the local model.
