# InHouseTX — Project Overview

**PayPal AI Spending Intelligence**  
**Tagline:** Understand Every Transaction. Make Every Payment Count.

## Executive summary

InHouseTX is a financial-intelligence hackathon prototype that connects a PayPal Sandbox checkout workflow with explainable transaction categorisation, currency-aware spending analytics, unusual-activity signals and grounded financial insights.

It extends the original InHouseTX transaction-categorisation project while retaining its attribution and MIT license.

## The problem

Payment histories often show merchant descriptors and amounts without explaining what those records may represent or how spending changes over time. Users can be left manually grouping purchases, comparing periods and searching for unusual patterns.

InHouseTX explores a workflow where machine learning organises transaction descriptions and transparent backend calculations provide the financial context.

## Product workflow

1. A signed-in user creates a PayPal Sandbox order from the application.
2. The buyer approves the order using PayPal's JavaScript SDK.
3. The Flask backend captures the order through PayPal Orders v2 and verifies provider-side status and payment details.
4. The application persists and categorises the transaction.
5. The user can inspect the prediction rationale, correct a category, explore analytics and budgets, review unusual activity, and ask questions about recorded spending.

CSV imports and seeded demo records support non-PayPal testing. Their source labels are preserved so they are never misrepresented as PayPal events.

## Core product capabilities

- Server-side PayPal Sandbox order create, lookup and capture paths.
- Transaction categorisation with TF-IDF + Logistic Regression.
- Model probability and feature-contribution explanations.
- Low-confidence review and human category correction.
- Explicit candidate model evaluation/retraining workflow.
- Currency-separated analytics, date/category/merchant filtering and budgets.
- Explainable unusual amount/frequency signals.
- Deterministic insights based on persisted financial facts.
- Responsive same-origin browser application.

## Trust and safety principles

- Payment success is based on server-side PayPal verification, not a browser redirect.
- Different currencies are reported separately rather than summed together.
- Synthetic records and CSV imports keep their provenance labels.
- Model output is advisory and has known limitations.
- Unusual activity is not a fraud finding.
- The application does not initiate payments autonomously.

## Technology

Python, Flask, SQLAlchemy, SQLite, PostgreSQL support via Psycopg 3, PayPal REST Orders v2, PayPal OAuth 2.0, PayPal JavaScript SDK, scikit-learn, TF-IDF, Logistic Regression, HTML, CSS, JavaScript and pytest.

See [TECHNOLOGY_STACK.md](TECHNOLOGY_STACK.md) for the verified stack.

## Project lineage

The original project, **InHouseTX — Automated AI-Based Financial Transaction Categorisation**, was developed by **Team Tech4Good** for the **GHCI 2025 Hackathon**. The PayPal AI Hackathon 2026 branch adds the payment-connected application and financial intelligence features. See [HACKATHON_CHANGELOG.md](HACKATHON_CHANGELOG.md) for the distinction between original work and subsequent additions.

## Verification and limitations

The latest local UI report records 26 passing tests and desktop browser inspection using synthetic CSV rows. Automated PayPal provider tests use mocked HTTP responses. Actual Sandbox buyer approval and capture, external webhook delivery, production deployment, and complete tablet/mobile visual QA remain separate verification tasks.

The classifier was evaluated on a small synthetic dataset; its results do not establish real-world performance. InHouseTX is a hackathon prototype, not production financial software.

For setup, see the root [README](../README.md). For details, see [ARCHITECTURE](ARCHITECTURE.md), [AI/ML PIPELINE](AI_ML_PIPELINE.md), [PAYPAL INTEGRATION](PAYPAL_INTEGRATION.md), and [KNOWN LIMITATIONS](KNOWN_LIMITATIONS.md).
