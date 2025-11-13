from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import string
from nltk.corpus import stopwords
import nltk
from nltk.stem.porter import PorterStemmer
from fastapi.middleware.cors import CORSMiddleware

# -------------------------------
# Initialization
# -------------------------------
app = FastAPI(title="Spam Detection API", version="1.0")
ps = PorterStemmer()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Download required NLTK data (only once)
nltk.download('punkt')
nltk.download('stopwords')

# -------------------------------
# Load Model and Vectorizer
# -------------------------------
tfidf = pickle.load(open('vectorizer.pkl', 'rb'))
model = pickle.load(open('model.pkl', 'rb'))

# -------------------------------
# Define Input Schema
# -------------------------------
class Message(BaseModel):
    text: str

# -------------------------------
# Preprocessing Function (same as before)
# -------------------------------
def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)

    y = []
    for i in text:
        if i.isalnum():
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        y.append(ps.stem(i))

    return " ".join(y)


@app.post("/predict")
def predict_spam(data: Message):
    print(data)
    # Step 1: Preprocess
    transformed_sms = transform_text(data.text)
    
    # Step 2: Vectorize
    vector_input = tfidf.transform([transformed_sms])
    
    # Step 3: Predict
    result = model.predict(vector_input)[0]
    probability = model.predict_proba(vector_input)[0].tolist() if hasattr(model, "predict_proba") else None
    
    # Step 4: Return JSON Response
    return {
        "input": data.text,
        "prediction": "spam" if result == 1 else "not spam",
        "confidence": probability
    }