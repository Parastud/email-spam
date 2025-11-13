# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pickle
import re
import html
import os
import logging

import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# ---------------------------
# Initialization / logging
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("spam-detector-api")

app = FastAPI(title="Spam Detection API", version="1.0")

# Enable CORS for local testing / extension calls (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your extension's origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Download NLTK resources (once)
# ---------------------------
nltk.download("stopwords")
nltk.download("punkt")

STOPWORDS = set(stopwords.words("english"))
PS = PorterStemmer()

# ---------------------------
# Load model artifacts
# ---------------------------
VECTORIZER_PATH = "vectorizernew.pkl"
MODEL_PATH = "modelnew.pkl"

if not os.path.exists(VECTORIZER_PATH) or not os.path.exists(MODEL_PATH):
    logger.warning(f"Make sure '{VECTORIZER_PATH}' and '{MODEL_PATH}' exist in the working directory.")

try:
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)
    logger.info("Loaded TF-IDF vectorizer.")
except Exception as e:
    logger.exception("Error loading vectorizer.pkl")
    vectorizer = None

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    logger.info("Loaded model.")
except Exception as e:
    logger.exception("Error loading model.pkl")
    model = None

# Optional: if you stored other artifacts like scaler or domain columns, try to load them
scaler = None
sender_domain_cols = None
if os.path.exists("scaler_numeric.pkl"):
    try:
        with open("scaler_numeric.pkl", "rb") as f:
            scaler = pickle.load(f)
        logger.info("Loaded numeric scaler.")
    except Exception:
        logger.exception("Failed to load scaler_numeric.pkl")

if os.path.exists("sender_domain_cols.pkl"):
    try:
        with open("sender_domain_cols.pkl", "rb") as f:
            sender_domain_cols = pickle.load(f)
        logger.info("Loaded sender domain columns.")
    except Exception:
        logger.exception("Failed to load sender_domain_cols.pkl")

# ---------------------------
# Request / Response schema
# ---------------------------
class EmailIn(BaseModel):
    subject: str = ""
    body: str = ""
    # legacy: accept single text field
    text: str = None

class PredictionOut(BaseModel):
    input: str
    prediction: str
    confidence: list = None

# ---------------------------
# Preprocessing function (email-aware)
# ---------------------------
def transform_email_text(text: str) -> str:
    """
    Lowercase, mark urls/email/html/numbers, tokenize, remove stopwords, stem.
    Mirrors preprocessing used during training.
    """
    if not isinstance(text, str):
        text = str(text or "")

    # Unescape HTML entities
    text = html.unescape(text)
    text = text.lower()

    # Keep links & emails as special tokens
    text = re.sub(r"(https?://\S+)", " urltoken ", text)
    text = re.sub(r"www\.\S+", " urltoken ", text)
    text = re.sub(r"\S+@\S+", " emailtoken ", text)

    # Mark HTML tags presence (don't drop them entirely)
    text = re.sub(r"<[^>]+>", " htmltag ", text)

    # Replace digits with a token
    text = re.sub(r"\d+", " numtoken ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Tokenize on word characters
    tokens = re.findall(r"\b\w+\b", text)

    # Remove stopwords and stem
    filtered = [PS.stem(t) for t in tokens if t not in STOPWORDS]

    return " ".join(filtered)


# ---------------------------
# Prediction helper
# ---------------------------
def predict_from_text(combined_text: str):
    if vectorizer is None or model is None:
        raise RuntimeError("Model or vectorizer not loaded. Place 'vectorizer.pkl' and 'model.pkl' in the working directory.")

    # Preprocess
    cleaned = transform_email_text(combined_text)

    # Vectorize
    X = vectorizer.transform([cleaned])

    # Predict
    pred = model.predict(X)[0]
    proba = None
    try:
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)[0].tolist()
        elif hasattr(model, "decision_function"):
            # fallback: convert decision function to a pseudo-proba with sigmoid
            import numpy as np
            score = model.decision_function(X)
            prob_pos = 1 / (1 + np.exp(-score))
            proba = [1 - float(prob_pos), float(prob_pos)]
    except Exception as ex:
        logger.warning("Could not compute probabilities: %s", ex)
        proba = None

    return int(pred), proba


# ---------------------------
# API endpoints
# ---------------------------
@app.get("/")
def root():
    return {"status": "ok", "model_loaded": model is not None, "vectorizer_loaded": vectorizer is not None}


@app.post("/predict", response_model=PredictionOut)
def predict(email_in: EmailIn):
    try:
        # Accept either text field or subject+body
        if email_in.text:
            combined = email_in.text
        else:
            combined = (email_in.subject or "") + "\n\n" + (email_in.body or "")

        if not combined.strip():
            raise HTTPException(status_code=400, detail="Empty input text.")

        pred, proba = predict_from_text(combined)
        label = "spam" if pred == 1 else "not spam"

        return PredictionOut(input=combined[:5000], prediction=label, confidence=proba)
    except RuntimeError as re:
        logger.exception("Runtime error during prediction")
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        logger.exception("Unexpected error during prediction")
        raise HTTPException(status_code=500, detail="Prediction failed.")

# ---------------------------
# Run instructions:
# uvicorn app:app --reload --port 8000
# Make sure vectorizer.pkl and model.pkl exist in working directory.
# ---------------------------
