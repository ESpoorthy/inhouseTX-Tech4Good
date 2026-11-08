# Final Hackathon Completion Report

**Project:** InHouseTX — PayPal AI Spending Intelligence
**Working branch:** `codex/paypal-ai-hackathon-2026`
**Completion state:** Local implementation and submission materials prepared; external verification/publication steps remain.

## Delivered

The repository now contains a Flask/SQLAlchemy app, signed-cookie authentication and owner-scoped records, PayPal Sandbox Orders v2 create/get/capture and webhook verification paths, payment idempotency/audit handling, ML categorisation with confidence and feature rationale, recorded corrections, candidate-only retraining, currency-partitioned analytics, budgets, explainable unusual-spending heuristics, grounded insights, CSV import, labelled synthetic demo data, and a responsive no-build browser UI.

Documentation includes architecture/API/security/AI-ML/payments/deployment/testing/known limitations, setup and demo scripts, Devpost copy, recording checklist, Kiro specs/tasks, and this report. Existing Team Tech4Good attribution, MIT license, data, taxonomy, diagrams, legacy utilities and project documents remain present.

## Verification performed

- `python3 -m pytest -q` — **25 passed** (3.83 seconds).
- `python3 -m compileall -q api model scripts migrations tests` — passed.
- `node --check frontend/vanilla.js` — passed.
- `git diff --check` — passed.
- `python3 model/train.py` — completed and created `model/model.candidate.bin` plus `reports/model_evaluation.json`.
- Candidate evaluation: 240 synthetic descriptions; grouped holdout of 59; logistic regression selected with accuracy **0.7797**, macro F1 **0.7407**. These values describe only the synthetic benchmark and are not real-world model performance.
- The demo seeder was smoke-tested against a temporary SQLite database; it created 14 labelled synthetic transactions and no PayPal payment. The local browser app login screen was visually inspected. A full browser payment journey was not completed.

The training run printed Arrow hardware-query permission warnings from the constrained environment; it still completed successfully. PyPI/npm network installation could not be verified because package registry DNS was unavailable; installed dependencies were used for checks.

## Honest scope boundary

PayPal request, capture, failure, pending/completed reconciliation, webhook validation and duplicate handling are covered by mocked tests. No real Sandbox app credentials, buyer account or public HTTPS webhook endpoint were available, so an actual end-to-end PayPal checkout and webhook remain unverified. The app uses synthetic seed rows unless actual Sandbox events or CSV imports exist; no seeded row is a PayPal event.

There is no public deployment, public GitHub push, public demo video or Devpost submission. These require account/domain/credential access and owner-controlled external actions. The current branch remains local and `main` was preserved. No secrets or real financial records were added.

## Remaining action summary

1. Configure Sandbox application, buyer and webhook; perform and record a real Sandbox checkout/capture/webhook.
2. Review and authorize publication of the branch/repository.
3. Deploy over HTTPS with durable PostgreSQL, shared session/rate-limit strategy and managed secrets if a hosted demo is desired.
4. Record and publish a public video under the event’s duration rules; attach screenshots.
5. Complete and submit Devpost form before the owner-provided deadline: **13 November 2026, 1:30 AM IST**. Reconfirm this on the official event page at submission time.

See `docs/KNOWN_LIMITATIONS.md`, `docs/SUBMISSION_CHECKLIST.md`, and `submission/DEVPOST_SUBMISSION.md` for the action-level detail.
