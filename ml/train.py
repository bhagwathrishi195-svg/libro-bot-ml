import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from preprocess import normalize_text
from dataset_builder import build_dataset


def train_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "dataset.csv")

    if not os.path.exists(dataset_path):
        build_dataset(dataset_path)

    df = pd.read_csv(dataset_path)
    df["clean_text"] = df["text"].apply(normalize_text)
    df = df[df["clean_text"].str.len() > 0].drop_duplicates(subset=["clean_text"])

    X = df["clean_text"]
    y = df["intent"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    vectorizer = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=2)),
    ])

    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    classifier = LogisticRegression(
        C=5.0,
        max_iter=1500,
        class_weight="balanced",
        random_state=42,
    )
    classifier.fit(X_train_vec, y_train)

    y_pred = classifier.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)

    print(f"Total unique samples: {len(df)} | Train: {len(X_train)} | Test: {len(X_test)}")
    print(f"Held-out Test Accuracy: {acc:.4f}\n")
    print("Classification Report (Held-Out Test Set):")
    print(classification_report(y_test, y_pred, zero_division=0))

    model_path = os.path.join(base_dir, "model.pkl")
    vec_path = os.path.join(base_dir, "vectorizer.pkl")

    with open(model_path, "wb") as f:
        pickle.dump(classifier, f)
    with open(vec_path, "wb") as f:
        pickle.dump(vectorizer, f)

    print(f"Saved model -> {model_path}")
    print(f"Saved vectorizer -> {vec_path}")


if __name__ == "__main__":
    train_model()
