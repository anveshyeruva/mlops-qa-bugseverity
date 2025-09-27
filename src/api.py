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

def ensure_model_loaded() -> bool:
    global model
    try:
        if model is None and MODEL_PATH.exists():
            model = joblib.load(MODEL_PATH)
    except Exception as e:
        # Optional: log the error; keep model None
        print(f"[api] model load failed: {e}")
    return model is not None

@app.on_event("startup")
def load_model_on_startup():
    # Best-effort load; /health will ensure loading too
    ensure_model_loaded()

@app.get("/health")
def health():
    # Ensure model is loaded by the time health is queried
    loaded = ensure_model_loaded()
    return {"status": "ok", "model_loaded": loaded}

@app.post("/predict")
def predict(item: BugReport):
    if not ensure_model_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded. Train first: python src/train.py")
    text = f"{item.title or ''} {item.description or ''}".strip()
    pred = model.predict([text])[0]
    return {"severity": pred}

