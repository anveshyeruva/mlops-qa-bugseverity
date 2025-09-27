# src/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import joblib

app = FastAPI(title="Bug Severity API", version="0.1.0")

MODEL_PATH = Path("models/model.joblib")
model = None

class BugReport(BaseModel):
    title: str
    description: str

@app.on_event("startup")
def load_model():
    global model
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}

@app.post("/predict")
def predict(item: BugReport):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Train first: python src/train.py")
    text = f"{item.title or ''} {item.description or ''}".strip()
    pred = model.predict([text])[0]
    return {"severity": pred}

