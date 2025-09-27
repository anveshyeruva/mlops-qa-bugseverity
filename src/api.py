# src/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import joblib, os

app = FastAPI(title="Bug Severity API", version="0.1.0")

# Resolve repo root regardless of current working directory
ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "model.joblib"

model = None

class BugReport(BaseModel):
    title: str
    description: str

def ensure_model_loaded() -> bool:
    global model
    try:
        if model is None and MODEL_PATH.exists():
            print(f"[api] loading model from: {MODEL_PATH}")
            model = joblib.load(MODEL_PATH)
            print(f"[api] model loaded ok")
        elif not MODEL_PATH.exists():
            print(f"[api] model file not found at: {MODEL_PATH}")
    except Exception as e:
        # Log the error; keep model None so health shows false
        print(f"[api] model load failed: {e}")
    return model is not None

@app.on_event("startup")
def load_model_on_startup():
    print(f"[api] startup cwd={os.getcwd()}")
    print(f"[api] expected model path={MODEL_PATH}")
    ensure_model_loaded()

@app.get("/health")
def health():
    loaded = ensure_model_loaded()
    return {"status": "ok", "model_loaded": loaded}

@app.post("/predict")
def predict(item: BugReport):
    if not ensure_model_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded. Train first: python src/train.py")
    text = f"{item.title or ''} {item.description or ''}".strip()
    pred = model.predict([text])[0]
    return {"severity": pred}

