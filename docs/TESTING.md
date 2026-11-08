# Testing and verification

## Automated suite

Run from repository root:

```sh
python -m pytest -q
python -m compileall -q api model scripts migrations tests
node --check frontend/vanilla.js
git diff --check
```

The pytest suite covers local authentication/ownership/CSRF/rate-limit behavior, mocked PayPal order/capture/status/error/idempotency/webhook verification paths, currency-separated analytics, date filtering, CSV provenance, categorisation confidence/explanation/feedback, anomaly outputs, deterministic grounded insights, and candidate-model training. PayPal HTTP calls are mocked; this is not an end-to-end Sandbox verification.

## Local manual smoke test

1. Copy `.env.example` to `.env`, choose a unique `SECRET_KEY`, and start `python -m api.app`.
2. Open the local URL; sign up or use `python scripts/seed_demo.py` for labelled synthetic fixtures.
3. Confirm the demo data source labels and that analytics group currencies separately.
4. Correct a category; verify feedback and the updated category in the transaction detail.
5. Review/dismiss any generated anomaly and inspect its historical comparison.
6. Ask an insight question and confirm the answer names the covered range/currency or explains missing data.
7. With Sandbox credentials and a buyer test account, complete checkout, then confirm server-verified status and persisted transaction. This last flow remains unverified until credentials are supplied.

## Latest recorded results

The implementation run recorded 25 passing pytest cases, successful Python compileall, successful JavaScript syntax validation, and a clean `git diff --check`. These checks used the environment’s already installed dependencies. Dependency installation from PyPI/npm was not verified because package-host DNS/network access was unavailable. Re-run after any code edits and before publishing.

The synthetic grouped holdout classifier experiment contained 240 synthetic rows and 59 holdout rows. The first recorded run reported accuracy 0.7797 and macro F1 0.7407 for the selected logistic regression candidate. This is only a synthetic pattern benchmark. It is not a real transaction dataset, broad model validation, or a guarantee of production performance.

## Not verified

- A real PayPal Sandbox checkout/capture/webhook round trip.
- OpenAI provider response behavior using a live key.
- Cross-process persistence/rate limiting under a multi-worker host.
- Browser automation or full responsive/device accessibility audit.
- Clean dependency installation on a network-enabled environment.
- Production deployment.
