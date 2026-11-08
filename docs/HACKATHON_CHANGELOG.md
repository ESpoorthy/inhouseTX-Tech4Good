# PayPal AI Hackathon contribution log

## Branch scope

Work was performed on `codex/paypal-ai-hackathon-2026`; the repository’s `main` branch was preserved. No push, deployment, video publication, or Devpost submission was performed.

## Added for the hackathon

- Flask application foundation with database models, schema initialization, user sessions, owner-scoped access, health/readiness routes, CSV import and bounded APIs.
- PayPal Sandbox Orders v2 service with OAuth, create/get/capture, request idempotency keys, server-side payment reconciliation, webhook signature postback verification, event deduplication, and audit entries.
- Transaction categorisation service with TF-IDF probabilities and local feature contribution explanations; correction storage and candidate-only retraining/evaluation workflow.
- Currency-aware spending analytics, budget tracking, recurring merchant hints, per-user unusual-spending heuristics and deterministic grounded insights with optional LLM phrasing.
- Responsive dependency-free browser application for account creation, transactions, details, categorisation review, insights, analytics, anomaly review, Sandbox checkout, and settings.
- Synthetic-only demo fixtures, controlled CSV import, migrations, tests, Dockerfile and integration/deployment/demo/submission materials.

## Preserved foundation

Original Team Tech4Good project materials, MIT license, PDFs, dataset, feedback CSV, taxonomy configuration, preprocessing and model utilities, diagrams, and attribution are retained. A legacy training entry point was retained separately where the training workflow changed. This work log describes the code changes in this branch and does not assert that all original contributors participated in the new work.

## Verification limits

Unit/integration tests mock PayPal API interactions. No Sandbox credentials, external deployment, public repository push, public video, or Devpost submission were available/performed during this implementation. See `docs/KNOWN_LIMITATIONS.md` and final reports.
