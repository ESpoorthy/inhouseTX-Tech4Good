"""Train reproducible baseline models on the clearly synthetic dataset."""
from __future__ import annotations

import csv
import argparse
import hashlib
import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score, accuracy_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.naive_bayes import MultinomialNB

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic_training.csv"
MODEL = ROOT / "model" / "model.bin"
METRICS = ROOT / "reports" / "model_evaluation.json"


def _rows():
    with DATA.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _group(text):
    # Vendor-like first one or two words are held together across suffix variants.
    words = text.lower().split()
    return " ".join(words[:2])


def train_model(feedback_rows=None, promote=False, allow_regression=False):
    rows = _rows()
    texts = [r["description"] for r in rows]
    labels = [r["category"] for r in rows]
    groups = [_group(x) for x in texts]
    split = GroupShuffleSplit(n_splits=1, test_size=.25, random_state=42)
    train_idx, test_idx = next(split.split(texts, labels, groups))
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
    x_train = vectorizer.fit_transform([texts[i] for i in train_idx])
    x_test = vectorizer.transform([texts[i] for i in test_idx])
    y_train = [labels[i] for i in train_idx]
    y_test = [labels[i] for i in test_idx]
    feedback_rows = feedback_rows or []
    held_groups = {_group(texts[i]) for i in test_idx}
    excluded_feedback = sum(1 for text, _ in feedback_rows if _group(text) in held_groups)
    feedback_rows = [(text, category) for text, category in feedback_rows if _group(text) not in held_groups]
    valid_categories = set(labels)
    if any(category not in valid_categories for _, category in feedback_rows):
        raise ValueError("Feedback contains categories outside the active taxonomy.")
    if feedback_rows:
        extra_text = [str(text)[:500] for text, _ in feedback_rows]
        extra_labels = [category for _, category in feedback_rows]
        vectorizer.fit([texts[i] for i in train_idx] + extra_text)
        x_train = vectorizer.transform([texts[i] for i in train_idx] + extra_text)
        y_train += extra_labels
        x_test = vectorizer.transform([texts[i] for i in test_idx])
    candidates = {
        "multinomial_nb": MultinomialNB(),
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    }
    report = {"dataset": "data/synthetic_training.csv", "source_note": "Synthetic merchant-description patterns; not customer data.",
              "rows": len(rows), "train_rows": len(train_idx), "test_rows": len(test_idx), "split": "GroupShuffleSplit by vendor prefix; random_state=42", "models": {}}
    fitted = {}
    for name, estimator in candidates.items():
        estimator.fit(x_train, y_train)
        pred = estimator.predict(x_test)
        report["models"][name] = {"accuracy": accuracy_score(y_test, pred),
            "macro_f1": f1_score(y_test, pred, average="macro", zero_division=0),
            "classification_report": classification_report(y_test, pred, output_dict=True, zero_division=0)}
        fitted[name] = estimator
    winner = max(candidates, key=lambda name: report["models"][name]["macro_f1"])
    if promote and MODEL.exists():
        current_model, current_vectorizer, current_id = joblib.load(MODEL)
        current_pred = current_model.predict(current_vectorizer.transform([texts[i] for i in test_idx]))
        current_f1 = f1_score(y_test, current_pred, average="macro", zero_division=0)
        report["active_model_comparison"] = {"model_id": current_id, "macro_f1": current_f1}
        candidate_f1 = report["models"][winner]["macro_f1"]
        if candidate_f1 < current_f1 and not allow_regression:
            raise ValueError(f"Candidate macro F1 ({candidate_f1:.4f}) is below active model ({current_f1:.4f}); use --allow-regression only after manual review.")
    report["selected_model"] = winner
    report["selection_metric"] = "holdout macro F1"
    digest = hashlib.sha256(json.dumps({"synthetic": rows, "feedback": feedback_rows, "model": winner}, sort_keys=True).encode()).hexdigest()[:12]
    report["feedback_rows"] = len(feedback_rows)
    report["feedback_excluded_for_holdout_isolation"] = excluded_feedback
    report["model_id"] = f"inhouse-tx-{winner}-{digest}"
    MODEL.parent.mkdir(exist_ok=True)
    output = MODEL if promote else MODEL.with_name("model.candidate.bin")
    joblib.dump((fitted[winner], vectorizer, report["model_id"]), output)
    report["artifact"] = str(output.relative_to(ROOT)) if ROOT in output.parents else str(output)
    METRICS.parent.mkdir(exist_ok=True)
    METRICS.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return fitted[winner], vectorizer, report


def load_trained_components():
    model, vectorizer, _model_id = joblib.load(MODEL)
    return model, vectorizer


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a candidate model; pass --promote only after reviewing holdout metrics.")
    parser.add_argument("--promote", action="store_true", help="Promote this run to model/model.bin after training.")
    parser.add_argument("--allow-regression", action="store_true", help="Allow promotion even when holdout macro F1 is lower than the active model.")
    args = parser.parse_args()
    model, vectorizer, result = train_model(promote=args.promote, allow_regression=args.allow_regression)
    print(json.dumps({"model": result["selected_model"], "rows": result["rows"],
                      "test_rows": result["test_rows"], "artifact": result["artifact"],
                      "metrics": result["models"][result["selected_model"]]}, indent=2))
