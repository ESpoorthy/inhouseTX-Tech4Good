# AI and ML Pipeline

## Existing project foundation

Team Tech4Good's original project included a TF-IDF + LightGBM trainer, a small seven-row labeled CSV, taxonomy JSON, a prediction wrapper, SHAP/LIME claims in its README, and CSV feedback. The checked-in code did not include MiniLM or LIME. The old LightGBM trainer is preserved as `model/legacy_train.py`; the `main` branch remains untouched. Its original seven-row stratified training workflow is too small to use as the new app model without failure/overfitting risk.

## Hackathon model

The app uses a simple scikit-learn TF-IDF word unigram/bigram vectorizer with logistic regression probabilities. Training data is `data/synthetic_training.csv`, containing 240 labeled, synthetic merchant-description examples across Food & Dining, Fuel, Groceries, Shopping, Transport and Utilities. It is explicitly not customer data.

`model/train.py` holds out vendor-prefix groups (`GroupShuffleSplit`, random state 42), compares Multinomial Naive Bayes and logistic regression on the same holdout, chooses by macro F1, and writes a candidate artifact by default. Model explanations use the selected linear model's input TF-IDF × class coefficient contributions, which are faithful to the linear score; this is not SHAP or LIME. The API exposes the actual maximum class probability as confidence and flags values below `LOW_CONFIDENCE_THRESHOLD` (default 0.55).

## Measured result

Command: `python3 model/train.py`
Dataset: 240 synthetic examples; held-out set: 59 rows, separated by vendor-like prefix groups.
Multinomial Naive Bayes: accuracy 0.7458, macro F1 0.6956.
Logistic regression: accuracy 0.7797, macro F1 0.7407 (selected).

These are measurements on a small, generated pattern dataset only. They do **not** estimate real-world merchant recognition or customer financial performance. Class probabilities are not calibrated. Low-confidence results are flagged; the demo fixtures may carry synthetic labels and are visibly sourced as synthetic.

## Feedback and model updates

User category corrections persist the original category, confidence, model ID, corrected category, comment and timestamp in the database. Feedback never retrains the running model automatically. `scripts/retrain_model.py --feedback-ids <ID...>` allows an operator to select specific correction rows for a candidate training run, excludes feedback whose vendor prefix overlaps the synthetic holdout, and reports the count excluded. Candidate artifacts are not active by default. The script supports explicit `--promote` only after review and blocks promotion if holdout macro F1 regresses unless the operator explicitly passes `--allow-regression`.

## Limitations

Synthetic data has limited vocabulary and vendor coverage. The current categories are narrow and the score is not calibrated. Model quality should not be used for financial decisioning. Replace or supplement with properly licensed, representative, consented transaction data and validation before any real-world use.
