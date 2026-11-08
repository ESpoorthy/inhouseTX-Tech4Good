# Existing System Audit

**Repository inspected:** `ESpoorthy/inhouseTX-Tech4Good` (`main`, shallow clone; HEAD `7b7acc5`, dated 2025-11-22)
**Audit scope:** tracked source, configuration, CSV data, README, license, and repository tree. No application code was changed during the audit.

## Findings

| Area | Status | Evidence and limits |
|---|---|---|
| Flask API | Partially implemented | `api/app.py` defines `/predict`, `/explain`, and `/feedback`. It loads serialized model files at import time. No auth, validation, ownership, rate limiting, safe error mapping, or health endpoint is present. Existing serialized model files are absent from the repository tree, so startup currently depends on files generated separately. |
| Preprocessing | Implemented, minimal | `utils/preprocess.py` lowercases, strips non-ASCII alphanumeric characters, collapses spaces. No abbreviation expansion or transaction schema validation. |
| Classifier | Partially implemented | `model/train.py` trains TF-IDF bigrams + LightGBM from `dataset.csv`, reports macro F1/classification report/confusion matrix, writes `model.bin` and `tfidf.bin`. `model/inference.py` uses `predict_proba().max()`. No model metadata/version, calibration, or low-confidence threshold. The README's MiniLM option is not implemented in the inspected source. |
| Explainability | Partially implemented / unverified | `utils/explain.py` invokes SHAP TreeExplainer and returns `shap_values[0].tolist()`. Shape/compatibility and whether this explains useful transaction features are not validated. No LIME implementation found. |
| Taxonomy | Partially implemented | `taxonomy.json` has four categories and merchant keyword lists. `utils/config.py` reads it, but training/inference do not use it to constrain labels or validate feedback. |
| Feedback | Partially implemented, unsafe | API appends raw comma-separated values directly to `feedback.csv`; there is no validation, CSV escaping, identity, timestamp, original prediction, model version, or controlled retraining workflow. |
| Dataset | Present, demonstration scale | `dataset.csv` has 7 rows and columns `merchant_name, category`; four classes have counts 2,1,2,2. It is too small to substantiate model quality or robust generalisation. |
| Feedback data | Present, empty | `feedback.csv` has the same two-column header and zero data rows at audit time. |
| Tests/evaluation scripts | Missing as standalone suite | No test files or test configuration were found. Evaluation exists inline in training, but no recorded run or result was produced during this audit. |
| Frontend | Missing | No frontend assets, package manifest, or UI source found. |
| Persistence/auth | Missing | No database, migration, authentication, or user model found. |
| PayPal | Missing | No PayPal SDK/client, order/capture endpoints, webhook route, or integration configuration found. |
| Analytics/anomalies/AI agent | Missing | No persisted transaction analytics, anomaly detector, or LLM assistant found. |
| Deployment/security docs | Missing | No Dockerfile, deployment config, `.env.example`, dedicated security docs, or CI workflow found. `.gitignore` excludes `.env` and common Python artifacts. |

## Verification boundary

This is a source inspection, not a successful runtime verification. No tests were run because no test suite was found and the requested first step is the audit/specification gate. Inference and explainability are not claimed to run: model artifacts are absent, and dependency/runtime compatibility was not exercised. The README describes MiniLM, LIME, batch inference, and a more complete feedback loop beyond what the checked-in code implements.

## Immediate risks

1. API startup fails if model artifacts have not been trained in the expected working directory.
2. Relative paths (`dataset.csv`, `model.bin`, `feedback.csv`, `taxonomy.json`) make behavior dependent on the current directory.
3. Raw feedback writes can produce malformed CSV or injection-like spreadsheet content.
4. The dataset is far too small to support meaningful predictive or financial claims.
5. The app has no user isolation; adding transaction persistence before authentication would expose cross-user data risk.
6. PayPal capture and webhook handling must be designed around server-side verification and idempotency; no existing foundation implements either.
