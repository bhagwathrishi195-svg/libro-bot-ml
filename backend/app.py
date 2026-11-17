import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_DIR = os.path.join(ROOT_DIR, "ml")
sys.path.insert(0, ML_DIR)

from predict import LibroBotPredictor  # noqa: E402

app = Flask(__name__)
CORS(app)

bot = LibroBotPredictor(ml_dir=ML_DIR)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model": "word+char-tfidf-logreg",
        "num_intents": len(bot.model.classes_),
    })


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).strip()
    if not query:
        return jsonify({"intent": "fallback", "confidence": 0.0, "is_confident": False}), 400
    return jsonify(bot.classify_only(query))


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).strip()
    session_id = str(data.get("session_id", "default")).strip() or "default"

    if not query:
        return jsonify({"error": "Empty query"}), 400

    result = bot.respond(query, session_id=session_id)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
