# InHouseTX — PayPal AI Spending Intelligence

**Understand Every Transaction. Make Every Payment Count.**

InHouseTX extends Team Tech4Good’s original financial transaction categorisation project into a local, Sandbox-only PayPal spending intelligence demo. It connects server-verified PayPal Sandbox order captures to a transaction ledger, categorises transaction text with a TF-IDF classifier, exposes model confidence and feature explanations, and provides currency-separated analytics, heuristic unusual-spending alerts, budgets, human category corrections, and grounded spending answers.

This is a hackathon prototype. It does not connect to real PayPal accounts or process live payments. PayPal state is accepted only after the server calls PayPal; synthetic and CSV rows are explicitly labelled and are never represented as PayPal transactions.

## Existing foundation and new work

The original InHouseTX repository was created by **Team Tech4Good** for the GHCI 2025 Hackathon. This branch preserves its taxonomy, transaction preprocessing, API, model utilities, evaluation assets, feedback CSV, diagrams, and attribution. See the original PDFs and [LICENSE](LICENSE). New PayPal AI Hackathon work is documented in [docs/HACKATHON_CHANGELOG.md](docs/HACKATHON_CHANGELOG.md); this does not imply that all original contributors participated in the new work.

## Product design

The responsive UI was redesigned from an editable [Figma file](https://www.figma.com/design/f4BTFU5wEmutlA2FetAxoI). See [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md) and [reports/UI_UX_REDESIGN_REPORT.md](reports/UI_UX_REDESIGN_REPORT.md) for screen inventory, tokens, implementation notes, and verification.

## Features

- PayPal Sandbox Orders v2: server-side order creation, buyer approval through the PayPal JavaScript SDK, server-side capture/status lookup, capture idempotency, webhook signature verification via PayPal postback, event de-duplication, and payment audit entries.
- Per-user login/session, CSRF protection, ownership-scoped data, rate limiting, secure cookie controls, input limits, and security headers.
- Transaction categorisation with real classifier probabilities and interpretable TF-IDF feature contributions; low-confidence results are queued for review.
- User category corrections and an explicit candidate-model retraining workflow. Candidate models are not automatically promoted.
- Spending summaries and trends, partitioned by currency, with date/category/merchant/status/source filters, budgets, merchant recurrence hints, and spending anomalies.
- Deterministic, transaction-grounded insights. Optional OpenAI phrasing can be configured; the model does not calculate totals or initiate payments.
- Synthetic demo account and bounded CSV import, with provenance labels.
- Responsive browser interface served by Flask; no frontend package installation required.

The fallback categoriser is trained from the clearly synthetic `data/synthetic_training.csv` when no model artifact exists. It is a demo model and is not a financial-grade classifier. SHAP/LIME integrations in the original repository remain available as original utilities but are not required by this new inference path.

## Architecture and API

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md), [docs/AI_ML_PIPELINE.md](docs/AI_ML_PIPELINE.md), and [docs/ANALYTICS_AND_ANOMALIES.md](docs/ANALYTICS_AND_ANOMALIES.md). Key routes include `/api/paypal/orders`, `/api/paypal/orders/<order_id>/capture`, `/api/paypal/orders/<order_id>`, `/api/paypal/webhooks`, `/api/transactions`, `/api/analytics`, `/api/insights`, and `/api/health` / `/api/ready`.

## Local setup

Python 3.10+ is recommended. From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set SECRET_KEY to a unique random value. PayPal Sandbox credentials are optional for non-payment features.
python scripts/migrate.py
python -m api.app
```

Open `http://127.0.0.1:3001` (or the port printed by Flask). Configure `PORT` to change the port. The application refuses non-Sandbox PayPal mode. To create labelled demo records and a one-time local demo account:

```sh
python scripts/seed_demo.py
```

The script prints a one-time password; treat it as local demo access and rotate by re-running the script. It creates synthetic records only. Do not use personal financial data.

### Environment variables

See [.env.example](.env.example). Required for authentication security: `SECRET_KEY`. For checkout and live webhook verification against Sandbox: `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, and `PAYPAL_WEBHOOK_ID`; `PAYPAL_MODE` must remain `sandbox`. For optional model phrasing: set `AI_PROVIDER=openai`, `OPENAI_API_KEY`, and `OPENAI_MODEL`. Deterministic answers work without an AI key. Use a trusted HTTPS public webhook URL for PayPal configuration. Never put secrets in browser code or commit `.env`.

## Tests and model evaluation

```sh
python -m pytest -q
python -m compileall -q api model scripts migrations tests
node --check frontend/vanilla.js
python model/train.py
```

`python model/train.py` creates a candidate artifact and synthetic-data evaluation report; it does not replace the active model. Inspect the report and promote explicitly with `--promote`. See [docs/TESTING.md](docs/TESTING.md) and [docs/AI_ML_PIPELINE.md](docs/AI_ML_PIPELINE.md). Reported synthetic holdout results are not evidence of real-world accuracy.

## PayPal Sandbox and demo

Follow [docs/PAYPAL_INTEGRATION.md](docs/PAYPAL_INTEGRATION.md) and [docs/DEMO_SETUP.md](docs/DEMO_SETUP.md). Then use the judge-facing flow in [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md). Checkout cannot succeed without valid Sandbox app credentials and a buyer Sandbox account. No transaction in this repository’s current evidence has been verified against a live Sandbox account.

## Deployment and security

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) and [docs/SECURITY.md](docs/SECURITY.md). Docker and health-check configuration are provided for evaluation; deployment has not been performed. Use HTTPS, managed secrets, a persistent PostgreSQL database, secure cookies, and a configured HTTPS webhook endpoint before any public demo. This prototype is not designed for production financial services.

## Hackathon submission

The draft submission package is in [submission/DEVPOST_SUBMISSION.md](submission/DEVPOST_SUBMISSION.md); recording materials are in [submission/](submission/) and final checklist in [docs/SUBMISSION_CHECKLIST.md](docs/SUBMISSION_CHECKLIST.md). The application code and written material are prepared locally. Public GitHub push, public hosting, YouTube recording, and Devpost submission require account access and have not been performed.

## License and attribution

MIT License. Original project: **InHouseTX — Automated AI-Based Financial Transaction Categorisation**, Team Tech4Good, GHCI 2025 Hackathon. The original attribution and repository artifacts are retained. New hackathon changes are described separately.
