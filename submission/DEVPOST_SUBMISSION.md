# Devpost submission draft — InHouseTX

**Project name:** InHouseTX — PayPal AI Spending Intelligence

**Elevator pitch:** Understand every transaction. Make every payment count. Explainable AI turns PayPal Sandbox payment activity into clear categories, spending patterns and grounded financial insights.

## About the project

InHouseTX is a financial intelligence prototype that helps people make sense of payment activity. It connects a PayPal Sandbox checkout workflow to transaction categorisation, explainable model output, currency-aware spending analytics, unusual-activity signals and grounded financial summaries.

A transaction feed tells someone what was charged. InHouseTX aims to add the missing context: what a transaction may represent, how confident the model is, how spending is distributed, and which patterns may deserve a closer look.

The product combines server-verified PayPal Sandbox order capture with a local TF-IDF and Logistic Regression categoriser. Predictions include probability and feature contributions; users can correct category labels, explore spending by currency and period, inspect unusual amount or frequency patterns, and ask questions answered from persisted transaction facts. Synthetic seed data and CSV imports are explicitly labelled and are not represented as PayPal payments.

### Inspiration

People often see payment records as a stream of merchant names and amounts, with little explanation of what the spending means. The original InHouseTX project explored automated transaction categorisation. We extended that foundation toward a payment-connected intelligence workflow that connects verified Sandbox payment state to understandable categories and useful financial context.

### What it does

InHouseTX provides account-scoped access to a spending dashboard, transaction history, analytics, budgets, anomaly review, AI insights and PayPal Sandbox checkout. After the buyer approves an order, the backend captures and verifies it with PayPal before recording the transaction. The categoriser supplies a predicted category, confidence and model-feature rationale. People can submit corrections for review. Analytics use deterministic calculations and keep currencies separate. Unusual-activity signals are explainable and are not labelled as confirmed fraud.

### How we built it

The project retains the original Flask/Python InHouseTX foundation and Team Tech4Good attribution. The hackathon branch adds Flask/SQLAlchemy persistence, a server-side PayPal Orders v2 client, a PayPal JavaScript SDK checkout, webhook signature verification and event de-duplication, a responsive browser UI, transaction APIs, TF-IDF classification with linear feature explanations, feedback capture, candidate-only model evaluation, analytics, anomaly heuristics and grounded insight responses. The browser interface is served by Flask and does not require a separate frontend build.

### AI and PayPal technology requirement

The PayPal integration uses the PayPal REST API Orders v2 for server-side order creation, lookup and capture; PayPal OAuth 2.0 for server authentication; and the PayPal JavaScript SDK for buyer approval. The webhook endpoint uses PayPal's verify-webhook-signature API when a webhook ID and a reachable HTTPS endpoint are configured.

The AI/ML component uses scikit-learn TF-IDF features and Logistic Regression to classify transaction descriptions. It reports classifier probability and feature-based rationale. A deterministic insights service calculates financial facts from persisted records; optional OpenAI-compatible phrasing can explain those facts without calculating totals or initiating payments.

**Verification disclosure:** PayPal HTTP behavior is covered by mocked automated tests. A real Sandbox buyer-approval/capture/webhook round trip must not be claimed as complete until tested with configured Sandbox credentials. See the integration verification details below.

### Challenges

Payment status must come from PayPal's server API and verified webhook events rather than browser claims. Currency totals must remain partitioned. Explanations and confidence must reflect the classifier actually used, while synthetic examples cannot stand in for real-world model evaluation. We also had to preserve the original project attribution while clearly separating the 2025 foundation from the 2026 hackathon additions.

### What we learned

A credible financial AI experience needs data provenance, deterministic arithmetic, transparent model limitations and human review alongside model predictions. An unusual transaction is not proof of fraud, and a frontend approval redirect is not proof of payment capture.

### Accomplishments

The repository contains a modular Flask application, persistent account-scoped records, PayPal Sandbox integration paths, explainable categorisation, feedback review, currency-aware analytics, anomaly heuristics, grounded insights, synthetic demo fixtures, tests, setup documentation and an editable Figma design.

The latest local browser QA report records synthetic CSV import and review of the major desktop views. Tablet/mobile and direct pixel-level Figma comparison remain incomplete.

### What's next

Complete and record the real Sandbox checkout/capture/webhook test, finish responsive visual QA, deploy a public demo with managed secrets and persistent storage, and publish the short demonstration video.

### Built with

Python, Flask, SQLAlchemy, SQLite/PostgreSQL support, scikit-learn, TF-IDF, Logistic Regression, PayPal REST API Orders v2, PayPal JavaScript SDK, HTML, CSS and JavaScript.

## Links to add before submitting

- Public project repository: https://github.com/ESpoorthy/inhouseTX-Tech4Good
- Hosted demo: **Add the verified deployment URL, or provide reproducible local setup instructions if no hosted demo is available.**
- Public YouTube demo (under 3 minutes): **Add after recording and uploading.**
- Figma design: https://www.figma.com/design/f4BTFU5wEmutlA2FetAxoI

## Original project and hackathon contribution

InHouseTX began as **Automated AI-Based Financial Transaction Categorisation**, developed by **Team Tech4Good** for the **GHCI 2025 Hackathon**. The 2026 branch preserves the original project materials and attribution while adding the PayPal Sandbox flow, persistent application, expanded categorisation and feedback, analytics, budgets, anomaly heuristics, grounded insights and redesigned UI. The changelog documents these contributions separately and does not imply that every original contributor participated in the 2026 work.

## Integration verification disclosure

The code includes PayPal Sandbox order, capture, status and webhook-verification paths. Automated tests use mocked PayPal responses. The actual Sandbox end-to-end transaction and webhook delivery must be completed and recorded by the project owner before describing them as live-verified. Synthetic dashboard records and CSV imports are not PayPal events. No production/live payment processing is included.
