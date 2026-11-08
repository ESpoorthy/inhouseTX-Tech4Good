# Existing Architecture

## Verified structure

```text
main.py                 CLI-style train-and-predict entry point
api/app.py              Flask inference/explanation/feedback endpoints
model/train.py          TF-IDF + LightGBM training and local artifact loading
model/inference.py      single merchant-string prediction and max class probability
utils/preprocess.py     text normalization
utils/explain.py        SHAP TreeExplainer wrapper
utils/config.py         taxonomy JSON loader
dataset.csv             7 labeled merchant strings
feedback.csv            empty feedback file with merchant/category columns
taxonomy.json           four category keyword groups
diagrams/               architecture and pipeline images
```

## Current data flow

Training reads `dataset.csv` from the process working directory, normalizes merchant text, fits a TF-IDF vectorizer and LightGBM classifier, prints metrics, and serializes two artifacts in the repository root. The API loads those artifacts and taxonomy at module import. `/predict` normalizes one string and returns the predicted label and largest class probability. `/explain` returns raw SHAP values. `/feedback` appends submitted strings to a CSV file.

## Target evolution (proposed, not implemented)

Retain this classifier behind a modular categorization service. Add a Flask-compatible application layer, durable relational persistence, authenticated user isolation, a PayPal Sandbox service, transaction/analytics/anomaly services, and a browser UI. Keep payment state authoritative from PayPal server-side API responses and verified webhook events. Treat demonstration fixtures as explicitly synthetic and keep currency totals partitioned by currency. The detailed target and acceptance criteria are in `.kiro/specs/paypal-inhouse-tx/`.
