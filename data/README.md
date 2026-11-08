# Data assets

- `synthetic_training.csv`: synthetic labelled examples used by the current TF-IDF + Logistic Regression pipeline.
- `legacy_merchant_dataset.csv`: the original seven-row merchant/category dataset retained for historical reproducibility; it is not the current model's training set.
- `taxonomy.json`: preserved category and merchant-keyword reference used by taxonomy-loading helpers.
- `archive/legacy_feedback.csv`: empty legacy feedback placeholder retained for provenance only. Current feedback is persisted in the database.

Do not add real PayPal credentials, private transaction exports, or personally identifying financial data here.
