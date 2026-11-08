# Technology Stack

This page records the technologies used by the current InHouseTX hackathon branch and the role each plays. It intentionally excludes tools that were considered but are not part of the implementation.

| Layer | Technology | Responsibility |
|---|---|---|
| Runtime | Python 3.10+ | Application and ML runtime |
| Web/API | Flask | Same-origin application, JSON API, session handling and static frontend serving |
| Persistence | SQLAlchemy | User, transaction, payment, feedback, budget, anomaly and audit data models |
| Local database | SQLite | Reproducible local development and demo storage |
| Hosted database support | PostgreSQL via Psycopg 3 | Database URL support for hosted environments |
| Payments | PayPal REST API, Orders v2 | Server-side Sandbox order creation, lookup and capture |
| Payment authentication | PayPal OAuth 2.0 | Server-to-server REST API authentication |
| Checkout UI | PayPal JavaScript SDK | Buyer approval experience in the browser |
| Webhook verification | PayPal verify-webhook-signature API | Server-side signature verification and event reconciliation |
| Machine learning | scikit-learn | TF-IDF vectorisation, Logistic Regression and model evaluation |
| Feature representation | TF-IDF word unigrams/bigrams | Transaction text representation |
| Analytics | Python Decimal/date aggregation | Currency-separated spending totals and trends |
| Browser interface | HTML, CSS, vanilla JavaScript | Responsive frontend served by Flask; no separate frontend build is required |
| Testing | pytest | API, database, model and business-logic tests |
| Static checks | Python compileall, Node syntax check, Git diff check | Syntax and whitespace validation |
| Optional language-model phrasing | OpenAI-compatible API configuration | Optional rephrasing of aggregate, precomputed facts; deterministic mode works without a provider key |

## Important implementation boundaries

- PayPal integration is Sandbox-only; no Live payment processing is configured.
- The browser receives only the PayPal public Client ID. The REST Secret remains on the server.
- The current model is TF-IDF + Logistic Regression trained/evaluated using synthetic examples.
- Model explanations use linear feature contributions; do not describe the current path as SHAP/LIME-based.
- Core financial totals and insight facts are computed deterministically by the backend. An optional language model does not initiate payments or calculate financial totals.
- SQLite is the local default. PostgreSQL support does not mean a production database has already been deployed.

See [ARCHITECTURE.md](ARCHITECTURE.md), [AI_ML_PIPELINE.md](AI_ML_PIPELINE.md), and [PAYPAL_INTEGRATION.md](PAYPAL_INTEGRATION.md).
