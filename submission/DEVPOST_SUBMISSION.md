# Devpost submission draft — InHouseTX

**Project name:** InHouseTX — PayPal AI Spending Intelligence

**Tagline:** Understand Every Transaction. Make Every Payment Count.

**Short description:** Explainable AI turns PayPal Sandbox checkout events into transaction categories, spending patterns, and grounded financial insights.

## Inspiration

People often see payment records as a stream of merchant names and amounts, with little explanation of what the spending means. The original InHouseTX project explored automated categorisation. We extended that foundation toward a working PayPal Sandbox transaction-intelligence flow that connects payment verification to explainable categorisation and useful spending context.

## What it does

InHouseTX provides a Sandbox checkout flow and a transaction dashboard. After the buyer approves an order, the backend captures and verifies the order with PayPal before recording its status. The categorisation service predicts a category with classifier probability and a feature-based explanation. Users can correct a label, inspect currency-aware analytics and budgets, review unusual spending against a personal baseline, and ask questions answered from deterministic persisted-data calculations. Synthetic fixtures and CSV imports are visibly identified as such.

## How we built it

The project retains the original Flask/Python InHouseTX foundation and Team Tech4Good attribution. The hackathon branch adds Flask/SQLAlchemy persistence, a server-side PayPal Orders v2 client, webhook signature verification and de-duplication, a responsive browser UI, transaction APIs, TF-IDF classification with local explanation, feedback capture, controlled model candidate evaluation, analytics, anomaly heuristics, and grounded insight responses. The dashboard is dependency-free and served by Flask.

## Challenges

Payment status must come from PayPal’s server API and verified webhook events rather than browser claims. Currency totals must remain partitioned. Explanations and confidence must reflect the classifier, while synthetic examples cannot stand in for real-world model evaluation. Dependency installation was unavailable in the implementation environment, so the working local UI avoids a package download step.

## What we learned

A credible financial AI demo needs provenance, deterministic arithmetic, clear explanation, and human review alongside a model prediction. Unusual activity is not proof of fraud, and successful checkout is not established by a frontend redirect.

## Built with

Python, Flask, SQLAlchemy, scikit-learn, SQLite/PostgreSQL support, PayPal REST Orders v2, PayPal JavaScript SDK, HTML, CSS, JavaScript.

## Links to add before submitting

- Public project repository: **ACTION REQUIRED**
- Public hosted demo: **OPTIONAL / ACTION REQUIRED if available**
- Public YouTube demo (<3 minutes): **ACTION REQUIRED**
- Screenshots: **ACTION REQUIRED**

## Integration verification disclosure

The submitted code contains PayPal Sandbox order, capture, status, and webhook verification paths. Automated tests use mocked PayPal responses. A genuine Sandbox end-to-end transaction and webhook delivery have not yet been performed in this workspace; do not describe them as live-verified until the team completes and records that external check. The current local seeded dashboard data is synthetic, not PayPal activity. No production or real payment processing is included.
