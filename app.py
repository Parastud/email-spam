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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("spam-detector-api")

app = FastAPI(title="Spam Detection API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
nltk.download("stopwords")
nltk.download("punkt")

STOPWORDS = set(stopwords.words("english"))
PS = PorterStemmer()

VECTORIZER_PATH = "vectorizer.pkl"
MODEL_PATH = "model.pkl"

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

scaler = None
sender_domain_cols = None
class EmailIn(BaseModel):
    subject: str = ""
    body: str = ""
    text: str = None

class PredictionOut(BaseModel):
    input: str
    prediction: str
    confidence: list = None

def transform_email_text(text: str) -> str:
    """
    Lowercase, mark urls/email/html/numbers, tokenize, remove stopwords, stem.
    Mirrors preprocessing used during training.
    """
    if not isinstance(text, str):
        text = str(text or "")

    text = html.unescape(text)
    text = text.lower()

    text = re.sub(r"(https?://\S+)", " urltoken ", text)
    text = re.sub(r"www\.\S+", " urltoken ", text)
    text = re.sub(r"\S+@\S+", " emailtoken ", text)
    text = re.sub(r"<[^>]+>", " htmltag ", text)
    text = re.sub(r"\d+", " numtoken ", text)
    text = re.sub(r"\s+", " ", text).strip()
    tokens = re.findall(r"\b\w+\b", text)

    filtered = [PS.stem(t) for t in tokens if t not in STOPWORDS]

    return " ".join(filtered)


def predict_from_text(combined_text: str):
    if vectorizer is None or model is None:
        raise RuntimeError("Model or vectorizer not loaded. Place 'vectorizer.pkl' and 'model.pkl' in the working directory.")

    cleaned = transform_email_text(combined_text)

    X = vectorizer.transform([cleaned])

    pred = model.predict(X)[0]
    proba = None
    try:
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)[0].tolist()
    except Exception as ex:
        logger.warning("Could not compute probabilities: %s", ex)
        proba = None
    return int(pred), proba

@app.get("/")
def root():
    return {"status": "ok", "model_loaded": model is not None, "vectorizer_loaded": vectorizer is not None}


@app.post("/predict", response_model=PredictionOut)
def predict(email_in: EmailIn):
    try:
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