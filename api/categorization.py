from __future__ import annotations

import csv
import json
from pathlib import Path
from datetime import datetime, timezone

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "model" / "model.bin"
SYNTHETIC = ROOT / "data" / "synthetic_training.csv"


class Categorizer:
    """Linear TF-IDF model with faithful per-token linear contribution explanations."""
    def __init__(self, threshold=0.55):
        self.threshold = threshold
        self.model_id = "inhouse-tx-logreg-v1"
        with (ROOT / "taxonomy.json").open(encoding="utf-8") as taxonomy_file:
            self.taxonomy = json.load(taxonomy_file)
        self.categories = list(self.taxonomy.get("categories", {}).keys())
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
        self.model = None
        if ARTIFACT.exists():
            try:
                self.model, self.vectorizer, self.model_id = joblib.load(ARTIFACT)
                self.categories = list(self.model.classes_)
            except Exception:
                self.model = None
        if self.model is None:
            texts, labels = self._load_synthetic()
            matrix = self.vectorizer.fit_transform(texts)
            self.model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
            self.model.fit(matrix, labels)
            self.categories = list(self.model.classes_)

    def _load_synthetic(self):
        with SYNTHETIC.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        return [r["description"] for r in rows], [r["category"] for r in rows]

    def predict(self, text: str):
        clean = " ".join(str(text or "")[:500].lower().split())
        vec = self.vectorizer.transform([clean])
        probs = self.model.predict_proba(vec)[0]
        idx = int(np.argmax(probs))
        category, confidence = str(self.model.classes_[idx]), float(probs[idx])
        # For this linear classifier, local feature x coefficient contributions are exact.
        contributions = vec.multiply(self.model.coef_[idx]).toarray()[0]
        names = self.vectorizer.get_feature_names_out()
        top = sorted(((names[i], float(contributions[i])) for i in np.argsort(contributions)[::-1]
                      if contributions[i] > 0), key=lambda item: item[1], reverse=True)[:5]
        return {"category": category, "confidence": confidence,
                "explanation": {"method": "linear_tfidf_contributions", "features": [
                    {"feature": token, "contribution": round(value, 4)} for token, value in top
                ], "summary": ("Matched transaction text features: " + ", ".join(x[0] for x in top)) if top
                             else "The model selected this category from its learned patterns."},
                "model_id": self.model_id, "classified_at": datetime.now(timezone.utc).isoformat(),
                "review_required": confidence < self.threshold}
