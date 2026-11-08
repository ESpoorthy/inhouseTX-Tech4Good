# Requirements — InHouseTX PayPal AI Spending Intelligence

**Status:** Approved implementation baseline. Implementation has been completed locally on `codex/paypal-ai-hackathon-2026`; consult tasks.md and final reports for verification and open external actions.

## Product objective

Extend the existing InHouseTX Flask/Python project into a Sandbox-only PayPal transaction intelligence demo. Preserve and wrap the existing TF-IDF + LightGBM foundation where technically viable. Tagline: “Understand Every Transaction. Make Every Payment Count.”

## Users and stories

- As a signed-in user, I can see only my own transactions and financial summaries.
- As a user, I can create and approve a PayPal Sandbox checkout, then see a transaction only after backend verification confirms its state.
- As a user, I can review a transaction’s category, model confidence, and understandable explanation, and correct an incorrect label.
- As a user, I can explore spending by period, currency, category, and merchant and see unusual activity with its comparison basis.
- As a user, I can ask questions about my stored activity and receive answers grounded in deterministic analytics.
- As a judge, I can distinguish verified Sandbox events from synthetic demo fixtures and follow a repeatable demonstration.
- As an operator, I can configure Sandbox credentials and model settings without committing secrets.

## Functional requirements and acceptance criteria

### Identity and data
- FR-1: Every private API operation requires authentication and enforces record ownership. **Accept:** unauthenticated requests are rejected; user A cannot read or mutate user B's records.
- FR-2: Persist a unified transaction with internal ID, user ID, PayPal order/capture IDs when applicable, amount, currency, description, merchant, event/payment timestamps, status, category, confidence, explanation, model ID, source, and creation time. **Accept:** database constraints and API schemas validate required fields; source explicitly distinguishes verified Sandbox from synthetic/imported data.
- FR-3: Store amounts in decimal-safe form and aggregate only within a currency unless an explicit documented conversion source/rate is added. **Accept:** multi-currency summaries are partitioned by currency.

### PayPal Sandbox
- FR-4: Backend creates Sandbox orders and returns only the data needed by the client approval flow. **Accept:** malformed amounts/currencies fail validation; client secrets never appear in responses or frontend bundles.
- FR-5: Backend captures an approved order idempotently and verifies the resulting PayPal response before persisting payment state. **Accept:** repeat capture returns/reconciles the existing result without duplicate transactions; failed/pending/cancelled states remain truthful.
- FR-6: Webhook endpoint verifies event authenticity using the current supported PayPal verification procedure and deduplicates event IDs. **Accept:** invalid signature is rejected; replayed event does not duplicate or regress state.
- FR-7: Record minimally necessary payment audit events without secrets or sensitive descriptions in logs. **Accept:** audit records link external IDs and state transitions, with restricted access.
- FR-8: No live payment processing. **Accept:** configuration is Sandbox-only for this project; any non-Sandbox environment is refused by the demo configuration.

### Categorisation and feedback
- FR-9: A categorization service reuses the existing classifier and returns category, actual model probability/confidence (or explicit unavailable state), explanation, relevant text features, model ID, and timestamp. **Accept:** invalid input is rejected; low confidence is flagged for review; no synthetic confidence is emitted.
- FR-10: User corrections persist original prediction, corrected category, user feedback, timestamp, and model version. **Accept:** taxonomy validation and ownership checks apply; feedback is not silently written into a malformed CSV.
- FR-11: Retraining is a controlled offline/operator action over reviewed data. **Accept:** user feedback alone never changes the active model automatically; evaluation artifact/version is recorded.

### Analytics and anomalies
- FR-12: Provide total, count, average, frequency, category/merchant summaries, daily/weekly/monthly trends, budget utilization, and date/category/merchant/currency/status filters. **Accept:** date boundaries are explicit and empty results are valid; each aggregate identifies period and currency.
- FR-13: Flag unusually large/frequent/repeated/category-spike/merchant-pattern transactions using explainable baselines. **Accept:** output includes score, severity, historical comparison, explanation and suggested review action; it never asserts fraud solely from anomaly score.

### AI insights
- FR-14: Assistant obtains facts only through authorized stored analytics and deterministic calculations. **Accept:** totals equal analytics results; unavailable facts are stated as unavailable; answers identify date range and currency.
- FR-15: LLM, if configured, may phrase grounded facts but cannot calculate totals or initiate/approve/capture payments. **Accept:** transaction text is treated as untrusted data; prompt injection attempts do not change system policy or payment state.

### Dashboard and demo
- FR-16: Provide landing/auth, overview, transaction list/detail, analytics, anomaly review, insights, feedback review, Sandbox checkout, and integration settings/status pages. **Accept:** every page has loading, empty, success and error states appropriate to its operations, and is responsive/accessibility reviewed.
- FR-17: Clearly label synthetic fixtures and show PayPal-processed status only when supported by a verified Sandbox API/webhook record. **Accept:** no frontend success claim can create or alter authoritative payment status.
- FR-18: Demo covers dashboard, Sandbox approval/capture, persisted verified transaction, categorization/explanation, analytics, anomaly review, grounded assistant query, and category correction.

## Non-functional requirements

- NFR-1 Security: TLS in deployment, server-only secrets, secure session/token handling, user isolation, input validation, rate limits, restrictive CORS, safe errors, and no secret/financial payload leakage in logs.
- NFR-2 Reliability: payment processing and webhook handling are idempotent; persistence is transactional around verified state changes.
- NFR-3 Maintainability: modular services and versioned schemas; preserve Flask/Python unless audit-driven need emerges.
- NFR-4 Accessibility/responsiveness: keyboard navigable, contrast checked, usable at mobile and desktop widths.
- NFR-5 Truthfulness: no claims of model performance, PayPal integration, or test success without evidence.
- NFR-6 Privacy: collect only demo-required data; clearly label Sandbox and synthetic records.

## Error handling

Return stable, non-sensitive error codes for validation, authentication, authorization, PayPal rejection/timeout, duplicate/idempotent replay, persistence failure, model unavailability, and upstream AI unavailability. Never translate upstream failure into payment success. Preserve retryability for transient PayPal failures and report unresolved/pending states accurately.

## Testing requirements

Automated coverage is required for PayPal order/capture/webhook/idempotency, preprocessing/prediction/threshold/explanation/feedback, analytics currency/date/empty cases, auth/ownership/input/secret leakage, and AI grounding/date/prompt injection. Use mocked PayPal/LLM boundaries for deterministic tests plus Sandbox end-to-end verification when credentials are available. Preserve existing tests; report exactly what ran and its result.

## Security requirements

No real payment mode; secrets in environment/secret store only; webhook authenticity checked; capture and events idempotent; all user records scoped server-side; transaction text and CSV imports untrusted; no automatic model promotion; no LLM payment tools; redact logs; dependency and deployment configuration reviewed.

## Demo requirements

The complete 12-step workflow in `docs/DEMO_SCRIPT.md` must be reproducible with Sandbox setup instructions, seeded synthetic fixtures labeled as such, and no fabricated successful payment or model metric.
