"""Preserved trainer for the original seven-row GHCI dataset.

This historical baseline is separate from the current PayPal prototype training pipeline.
"""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from lightgbm import LGBMClassifier

from utils.preprocess import normalise_text

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "legacy_merchant_dataset.csv"
ARTIFACT_DIR = ROOT / "model"


def train_model():
    df = pd.read_csv(DATASET)
    df["clean"] = df["merchant_name"].apply(normalise_text)
    X, y = df["clean"], df["category"]
    tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
    X_vec = tfidf.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X_vec, y, test_size=0.2, random_state=42, stratify=y
    )
    model = LGBMClassifier(objective="multiclass", learning_rate=0.1, n_estimators=300)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    print("Macro F1 Score:", f1_score(y_test, pred, average="macro"))
    print("Classification Report:")
    print(classification_report(y_test, pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, pred))
    joblib.dump(model, ARTIFACT_DIR / "legacy_model.bin")
    joblib.dump(tfidf, ARTIFACT_DIR / "legacy_tfidf.bin")
    return model, tfidf


def load_trained_components():
    return (joblib.load(ARTIFACT_DIR / "legacy_model.bin"),
            joblib.load(ARTIFACT_DIR / "legacy_tfidf.bin"))
