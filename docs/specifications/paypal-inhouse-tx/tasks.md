# Implementation Tasks — InHouseTX PayPal AI Spending Intelligence

**Status:** Implementation substantially complete locally on `codex/paypal-ai-hackathon-2026`; external Sandbox/deployment/publication actions remain. Phase 0 and specification work were approved by the project owner.

## Phase 0 — Existing repository audit (complete)
- [x] Inspect repository tree, README, license, requirements, Flask API, ML pipeline, preprocessing, explainability, taxonomy, feedback, dataset, tests, and frontend presence.
- [x] Produce audit, architecture, and feature gap documents.
- [x] Record verification boundary and risks; no test suite found, no tests run.

## Phase 1 — Requirements/specification (draft complete; review gate)
- [x] Draft requirements, architecture/database/API/security design, and phased tasks.
- [x] Review consistency and approve scope before broad code changes (owner authorized full implementation).
- [x] Verify current official PayPal Orders/Capture/Webhooks API formats and supported SDK choices before integration implementation.
- [x] Select signed-cookie authentication, SQLAlchemy SQLite/PostgreSQL support, single-service deployment and Sandbox/local demo scope.

## Phase 2 — Backend foundation and persistence
- [x] Create branch `codex/paypal-ai-hackathon-2026`; preserve `main`.
- [x] Add app factory/config, initial migration/schema setup, database models, error handling, health/readiness.
- [x] Add authentication, CSRF and owner-scoped transaction access.
- [x] Add transaction provenance and Decimal/currency-safe model.
- [x] Add backend unit/integration/security tests and model training/evaluation coverage (no pre-existing test suite existed).

## Phase 3 — PayPal Sandbox
- [x] Implement server-side Sandbox OAuth/configuration, order create/get/capture (mock-verified).
- [x] Add capture idempotency and verified status persistence/audit (mock-verified).
- [x] Add webhook authenticity verification and event deduplication/reconciliation (mock-verified).
- [x] Add mocked success/failure/pending/replay tests and Sandbox setup instructions. Live Sandbox round trip remains pending.

## Phase 4 — ML categorisation
- [x] Add modular inference service; preserve original model utilities.
- [x] Add model identifiers, actual probabilities and configurable low-confidence review threshold.
- [x] Provide readable TF-IDF feature contributions for active path; original SHAP/LIME utilities remain optional and are not a dependency.
- [x] Persist human correction and add candidate-only offline retraining/evaluation workflow.

## Phase 5 — Analytics and anomalies
- [x] Implement deterministic date/category/merchant/status summaries grouped by currency.
- [x] Add trends/frequency/category comparisons, budget utilization and merchant recurrence hints.
- [x] Add explainable per-user heuristic anomaly baselines and insufficient-history behavior.
- [x] Test currency partitioning, boundaries, empty data, and anomaly baselines.

## Phase 6 — AI insights assistant
- [x] Define deterministic analytics facts and prompt/data boundaries.
- [x] Add optional language model phrasing; deterministic calculation remains server side. Live provider remains unverified.
- [x] Add grounding, date/currency citation, unavailable-data, and prompt-injection tests.

## Phase 7 — Frontend/dashboard
- [x] Use dependency-free static frontend served by Flask.
- [x] Build responsive overview, transactions/detail, analytics, anomalies, insights, feedback, checkout, settings.
- [x] Add core loading/empty/error states and explicit synthetic/Sandbox/CSV provenance labels; full accessibility audit remains.
- [ ] Complete full live Sandbox checkout through webhook/user-visible reconciliation (external credentials and webhook required).

## Phase 8 — Security hardening
- [x] Implement/review auth/session, authorization, CSRF, input/file limits, CORS, rate limits, secret management and safe errors; deployment-level review remains.
- [x] Test no client-controlled payment status and cross-user access isolation.
- [x] Test webhook replay/idempotency and prompt injection; retention policy remains a deployment/product decision.

## Phase 9 — Integration tests and bug fixing
- [x] Run complete new suite; no original tests were present to preserve.
- [x] Exercise mocked PayPal paths. Live Sandbox flow awaits external configuration.
- [x] Record commands, results, limitations, and unresolved external checks.
- [x] Resolve test-discovered critical defects; no live integration verdict is possible before Sandbox credentials.

## Phase 10 — Deployment preparation
- [x] Add backend Dockerfile, dependency-free frontend, migration/health instructions and environment template.
- [x] Validate local container configuration statically; clean dependency installation and deployed startup remain unverified due network limits.

## Phase 11 — Documentation/demo
- [x] Update README while preserving original project and Team Tech4Good attribution.
- [x] Add/update PayPal, security, API, changelog, and demo documentation.
- [x] Add honest recording script/shot list; no fake screenshot/video or unverified PayPal success claim.
- [ ] Run complete PayPal demo after credentials/webhook are available; local synthetic-mode setup documented.

## Remaining external work
- [ ] Configure PayPal Sandbox and perform genuine order approval, capture and webhook verification.
- [ ] Deploy publicly and validate production-like persistence/HTTPS/webhook delivery.
- [ ] Publish public source/video and complete Devpost form after owner review.

## Phase exit reporting
At every phase close: list completed work and changed files, run relevant requested tests, report failures, update this checklist, and list remaining work. Do not advance past unresolved critical integration failures.
