import json
import os
import pickle
import sys
from preprocess import normalize_text, extract_entities
from response_engine import ResponseEngine, FALLBACK

CONFIDENCE_THRESHOLD = 0.22


class LibroBotPredictor:
    def __init__(self, ml_dir: str = None, threshold: float = CONFIDENCE_THRESHOLD):
        if ml_dir is None:
            ml_dir = os.path.dirname(os.path.abspath(__file__))
        self.threshold = threshold
        self.engine = ResponseEngine()

        with open(os.path.join(ml_dir, "model.pkl"), "rb") as f:
            self.model = pickle.load(f)
        with open(os.path.join(ml_dir, "vectorizer.pkl"), "rb") as f:
            self.vectorizer = pickle.load(f)

    def classify_only(self, query: str) -> dict:
        clean_q = normalize_text(query)
        if not clean_q:
            return {"intent": "fallback", "confidence": 0.0, "is_confident": False, "entities": {}}

        vec = self.vectorizer.transform([clean_q])
        if vec.nnz == 0:
            return {"intent": "fallback", "confidence": 0.0, "is_confident": False, "entities": {}}

        probs = self.model.predict_proba(vec)[0]
        best_idx = int(probs.argmax())
        predicted_intent = str(self.model.classes_[best_idx])
        confidence = round(float(probs[best_idx]), 4)
        entities = extract_entities(query)

        is_confident = confidence >= self.threshold
        return {
            "intent": predicted_intent if is_confident else "fallback",
            "raw_intent": predicted_intent,
            "confidence": confidence,
            "is_confident": is_confident,
            "entities": entities,
        }

    def respond(self, query: str, session_id: str = "default") -> dict:
        entities = extract_entities(query)

        # 1. Check if session is awaiting a multi-turn calculator input
        pending_reply = self.engine.handle_pending(session_id, query, entities)
        if pending_reply is not None:
            return {
                "intent": "calculator_followup",
                "confidence": 1.0,
                "is_confident": True,
                "entities": entities,
                "pending_mode": self.engine.get_pending_mode(session_id),
                "response": pending_reply,
            }

        # 2. Classify intent using the trained ML model
        pred = self.classify_only(query)
        intent = pred["intent"]

        if not pred["is_confident"] or intent == "fallback":
            return {
                "intent": "fallback",
                "confidence": pred["confidence"],
                "is_confident": False,
                "entities": entities,
                "pending_mode": None,
                "response": FALLBACK,
            }

        reply = self.engine.generate(intent, query, entities, session_id=session_id)
        return {
            "intent": intent,
            "confidence": pred["confidence"],
            "is_confident": True,
            "entities": entities,
            "pending_mode": self.engine.get_pending_mode(session_id),
            "response": reply,
        }


if __name__ == "__main__":
    bot = LibroBotPredictor()
    queries = sys.argv[1:] or [
        "tell me fine for my 14 days overdue book",
        "libary timmings",
        "library kab khulti hai",
        "Where is Mechanical Engineering?",
        "What is the capital of France?",
    ]
    for q in queries:
        print(f"Query: {q}")
        print(json.dumps(bot.respond(q), indent=2, ensure_ascii=False))
        print("-" * 55)
