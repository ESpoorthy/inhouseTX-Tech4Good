# Feature Gap Analysis

| Product area | Existing foundation | Gap to target | Proposed phase |
|---|---|---|---|
| PayPal Sandbox | None | OAuth credentials, create/approve/capture flow, status verification, verified webhooks, event/capture idempotency, audit records | 3 |
| Unified transactions | Merchant/category CSV only | Persisted transaction, capture, user, currency, status, source, timestamps, prediction metadata | 2 |
| Existing ML | TF-IDF + LightGBM code | Isolated service, artifact/version metadata, input validation, confidence review threshold, safe explanation contract, tested feedback | 4 |
| Explainability | SHAP wrapper | Verify output compatibility and provide readable feature-level rationale; no claim of causal explanation | 4 |
| Analytics | None | Currency-aware period/category/merchant totals, trends, filters, budgets | 5 |
| Anomalies | None | Explainable statistical baselines; label unusual activity, never confirmed fraud | 5 |
| Insights assistant | None | Grounded answers over deterministic query results; LLM optional for language only; prompt injection defenses | 6 |
| UI | None | Responsive pages, loading/error/empty states, Sandbox checkout and clear demo-data provenance | 7 |
| Security | Debug Flask server, no access control | Auth, authorization, ownership, validation, rate limits, CORS, secret handling, audit, safe logs | 8 |
| QA | No tests discovered | Unit/integration/security tests and documented truthful results | 9 |
| Deployment/docs | README only | Reproducible setup, containers, migrations, health check, Sandbox guide, demo runbook | 10-11 |

## Dependencies and gates

- Database and identity model precede user-specific transaction routes.
- PayPal API formats and webhook verification procedure must be checked against current official documentation before implementation.
- Sandbox credentials and webhook registration are external setup dependencies; no credentials are present or should be committed.
- Existing model startup depends on generated artifacts; training/data limitations must be resolved or clearly surfaced before demo claims.
- AI insights depend on correct persisted analytics and must not calculate financial amounts with an LLM.
- Broad implementation should begin only after review of requirements/design/tasks and approval, as requested.
