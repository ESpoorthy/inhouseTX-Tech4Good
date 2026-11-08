import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from lightgbm import LGBMClassifier
import joblib

from utils.preprocess import normalise_text

def train_model():
    df = pd.read_csv("dataset.csv")
    df["clean"] = df["merchant_name"].apply(normalise_text)

    X = df["clean"]
    y = df["category"]

    tfidf = TfidfVectorizer(ngram_range=(1,2), min_df=2)
    X_vec = tfidf.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_vec, y, test_size=0.2, random_state=42, stratify=y
    )

    model = LGBMClassifier(
        objective="multiclass",
        learning_rate=0.1,
        n_estimators=300
    )

    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    macro = f1_score(y_test, pred, average="macro")

    print("Macro F1 Score:", macro)
    print("Classification Report:")
    print(classification_report(y_test, pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, pred))

    joblib.dump(model, "model.bin")
    joblib.dump(tfidf, "tfidf.bin")

    return model, tfidf


def load_trained_components():
    model = joblib.load("model.bin")
    tfidf = joblib.load("tfidf.bin")
    return model, tfidf
