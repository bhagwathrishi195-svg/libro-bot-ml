i issued the book on 14th feb 2026 its now 16 nov 2026 calculate fine for the student# LibroBot — MANIT Central Library (Self-Trained NLP Assistant)

A locally trained Machine Learning NLP assistant for the MANIT Central Library. It uses a Python **Word + Character TF-IDF + Logistic Regression** intent classifier, a custom NLP entity extractor (`days`, `books`, `date`, `subject`, `floor`, `day`, `category`), and a dynamic response engine.

## Setup and execution

### 1. Install dependencies

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
# venv\\Scripts\\activate

pip install -r requirements.txt
```

### 2. Generate the dataset and train the model

Run these commands from the project root:

```bash
python ml/dataset_builder.py
python ml/train.py
```

Training generates `ml/dataset.csv`, `ml/model.pkl`, and `ml/vectorizer.pkl`.

### 3. Evaluate and test predictions

```bash
python ml/evaluate.py
python ml/predict.py "tell me fine for my 14 days overdue book"
```

### 4. Start the local Flask backend

```bash
python backend/app.py
```

The API runs at `http://127.0.0.1:5000`.

### 5. Run the frontend

Open a second terminal from the project root:

```bash
python -m http.server 8000 --directory frontend
```

Then open `http://127.0.0.1:8000` in your browser.

### 6. Run the automated Node test suites

Keep the Flask backend running, then run:

```bash
node tests/harness.js
node tests/heldout.js
```

## Notes

- Train the model before starting the backend because the backend loads the generated `.pkl` model files at startup.
- The frontend sends chat requests to `http://127.0.0.1:5000/chat`.
- The project uses a locally trained classifier; no external AI API is required.
