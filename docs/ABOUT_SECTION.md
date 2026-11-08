# About InHouseTX

## Understand every transaction. Make every payment count.

InHouseTX is a financial intelligence prototype that helps people make sense of payment activity. It connects a **PayPal Sandbox checkout workflow** to transaction categorisation, explainable model output, currency-aware spending analytics, unusual-activity signals, and grounded financial summaries.

A transaction feed tells someone what was charged. InHouseTX aims to add the missing context: what a transaction may represent, how confident the model is, how spending is distributed, and which patterns may deserve a closer look.

### The problem we are exploring

Payment histories can be difficult to interpret at a glance. Merchant descriptors are inconsistent, spending is spread across categories, and a list of amounts rarely explains how behaviour changes over time. InHouseTX explores how careful automation can turn transaction records into understandable information without hiding uncertainty or taking financial decisions away from the user.

### What the product does

- **Connects a payment workflow:** creates PayPal Sandbox orders on the server and records a transaction only after server-side capture/status checks.
- **Explains transaction categories:** predicts a category with a model probability and feature-level rationale from a TF-IDF linear classifier.
- **Keeps people in the loop:** allows category corrections and stores feedback for review before a candidate model can be promoted.
- **Surfaces spending context:** calculates category, merchant and time-based summaries while keeping different currencies separate.
- **Highlights unusual patterns:** detects selected amount or frequency deviations against available history; these are review signals, not fraud findings.
- **Answers from recorded facts:** produces deterministic insights from the user's persisted transaction data, with optional language-model phrasing that does not calculate totals or initiate payments.

### Our mission

Make financial activity more transparent, understandable and actionable through responsible, explainable AI.

### Our principles

1. **Trust the source:** payment state comes from server-side PayPal verification, not a frontend claim.
2. **Show the evidence:** predictions include confidence and model-derived feature contributions.
3. **Keep the human in control:** feedback is reviewed; the model does not autonomously make payments.
4. **Respect provenance:** Sandbox payments, CSV imports and synthetic demo data are visibly distinct.
5. **Never overstate a signal:** an unusual transaction is not automatically fraud, and synthetic evaluation is not real-world validation.

### Project origins and contribution

InHouseTX began as **Automated AI-Based Financial Transaction Categorisation**, developed by **Team Tech4Good** for the **GHCI 2025 Hackathon**. The original project explored local transaction-text categorisation and a configurable taxonomy.

For the PayPal AI Hackathon 2026, the codebase was extended with PayPal Sandbox Orders v2 flows, persistent transaction records, account-scoped application features, an expanded ML workflow, feedback review, currency-aware analytics, anomaly heuristics, grounded insights and a responsive browser interface.

The repository's [hackathon changelog](HACKATHON_CHANGELOG.md) identifies the new work separately. This acknowledgement does not imply that every original contributor participated in the 2026 development.

### What InHouseTX is — and is not

InHouseTX is a hackathon prototype for exploring payment-connected financial intelligence. It is **not** a budgeting adviser, a fraud-detection authority, a credit decision system, or production financial software. Its current classifier is evaluated on a small synthetic dataset, and the PayPal end-to-end Sandbox checkout must be separately verified with configured credentials and a Sandbox buyer.

For implementation details, see [the architecture](ARCHITECTURE.md), [AI/ML methodology](AI_ML_PIPELINE.md), [PayPal integration](PAYPAL_INTEGRATION.md), and [known limitations](KNOWN_LIMITATIONS.md).
