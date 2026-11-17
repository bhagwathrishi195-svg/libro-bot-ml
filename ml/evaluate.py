import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)
from preprocess import normalize_text
from predict import LibroBotPredictor

ROBUSTNESS_SET_B = [
    ("Out-of-domain", "What is the capital of France?", ["fallback"]),
    ("Out-of-domain", "Tell me a joke", ["fallback"]),
    ("Out-of-domain", "Who won the cricket match yesterday?", ["fallback"]),
    ("Out-of-domain", "Explain quantum computing", ["fallback"]),
    ("Misspelled", "libary timmings", ["timings"]),
    ("Misspelled", "how to isue a book", ["issue"]),
    ("Misspelled", "fien calculation", ["fine"]),
    ("Misspelled", "where is mechnical engineering", ["subject"]),
    ("Hinglish", "library kab khulti hai", ["timings"]),
    ("Hinglish", "kitni book issue kar sakte hain", ["loan"]),
    ("Paraphrase", "I want to take a book home", ["issue"]),
    ("Paraphrase", "my book is late, what will I owe", ["fine"]),
    ("Paraphrase", "where do I sit and study quietly", ["facilities"]),
    ("Paraphrase", "can I read journals from my hostel", ["remote", "ejournals"]),
]


def evaluate():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(base_dir, "dataset.csv"))
    df["clean_text"] = df["text"].apply(normalize_text)
    df = df[df["clean_text"].str.len() > 0].drop_duplicates(subset=["clean_text"])

    _, X_test, _, y_test = train_test_split(
        df["clean_text"], df["intent"], test_size=0.20, random_state=42, stratify=df["intent"]
    )

    with open(os.path.join(base_dir, "model.pkl"), "rb") as f:
        model = pickle.load(f)
    with open(os.path.join(base_dir, "vectorizer.pkl"), "rb") as f:
        vectorizer = pickle.load(f)

    X_test_vec = vectorizer.transform(X_test)
    y_pred = model.predict(X_test_vec)

    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)

    print("=== Held-Out 20% Test Split Metrics ===")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1-Score : {f1:.4f}\n")
    print(classification_report(y_test, y_pred, zero_division=0))

    labels = sorted(df["intent"].unique())
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    print("=== Confusion Matrix Shape ===", cm.shape)

    print("\n=== Robustness Benchmark (Out-of-Domain, Misspelled, Hinglish, Paraphrase) ===")
    bot = LibroBotPredictor(ml_dir=base_dir)
    passed = 0
    for cat, q, expected in ROBUSTNESS_SET_B:
        res = bot.classify_only(q)
        ok = res["intent"] in expected
        if ok:
            passed += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {cat:<14} | {q:<38} -> got={res['intent']} (conf={res['confidence']:.2f}, exp={expected})")

    print(f"\nRobustness Score: {passed}/{len(ROBUSTNESS_SET_B)} ({passed/len(ROBUSTNESS_SET_B):.1%})")


if __name__ == "__main__":
    evaluate()
