# Email Spam Detector 📧🚫

A machine learning-powered email spam classifier with a **Flask API backend** and a **browser extension** for real-time detection. Trained on a labeled spam/ham dataset using scikit-learn.

---

## ✨ Features

- 🤖 ML model trained on a spam/ham email dataset (`spam_ham_dataset.csv`)
- 🧠 TF-IDF vectorization + classification via scikit-learn
- 🌐 Flask REST API serving real-time predictions
- 🔌 Browser extension for in-browser email classification
- 💾 Pre-trained model (`model.pkl`) and vectorizer (`vectorizer.pkl`) included — no retraining needed
- 🪟 One-click Windows launcher (`start.bat`)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| ML / Training | Python, scikit-learn, Jupyter Notebook |
| Text Processing | TF-IDF Vectorizer |
| API | Flask (Python) |
| Browser Extension | JavaScript |
| Dataset | `spam_ham_dataset.csv` |

---

## 📁 Project Structure

```
email-spam/
├── Jupiter file/       # Jupyter notebook — model training & evaluation
├── Extension/          # Browser extension source (JS)
├── app.py              # Flask API — loads model and serves predictions
├── model.pkl           # Pre-trained ML classifier
├── vectorizer.pkl      # Pre-trained TF-IDF vectorizer
├── spam_ham_dataset.csv# Labeled training dataset
└── start.bat           # Windows script to launch the Flask server
```

## 🚀 Getting Started

### Prerequisites

- Python >= 3.8
- pip
- Google Chrome (for the browser extension)

### Installation

```bash
# Clone the repository
git clone https://github.com/Parastud/email-spam.git
cd email-spam

# Install Python dependencies
pip install flask scikit-learn pandas numpy
```

### Running the Flask API

**On Windows** — simply double-click `start.bat`, or run:

```bash
python app.py
```

The API will start at `http://localhost:5000`.

### API Usage

Send a POST request with the email text to get a prediction:

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"email": "Congratulations! You have won a free prize. Click here now."}'
```

**Response:**
```json
{
  "prediction": "spam",
  "confidence": 0.97
}
```

---

## 🔌 Installing the Browser Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `Extension/` folder from this repo
5. The extension will appear in your toolbar — click it to classify any email text

---

## 📓 Model Training (Optional)

To retrain the model yourself:

1. Open the Jupyter notebook inside `Jupiter file/`
2. Run all cells — this will train on `spam_ham_dataset.csv` and output new `model.pkl` and `vectorizer.pkl` files
3. Replace the existing `.pkl` files in the root directory

```bash
# Install Jupyter if needed
pip install notebook
jupyter notebook
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

> Built by [Parth Sharma](https://github.com/parastud)
