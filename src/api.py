# src/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import os
import joblib
from typing import Optional, Tuple, Any, Dict

from src.registry import load_stage_model

app = FastAPI(title="Bug Severity API", version="0.3.0")

# -------- Config --------
PREDICT_MODEL_SOURCE = os.getenv("PREDICT_MODEL_SOURCE", "local").lower()  # "local" | "registry"

ROOT = Path(__file__).resolve().parents[1]
LOCAL_MODEL_PATH = ROOT / "models" / "model.joblib"

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
MLFLOW_MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME", "bug-severity-clf")
MLFLOW_MODEL_STAGE = os.getenv("MLFLOW_MODEL_STAGE", "Production")

# -------- State --------
_LOCAL_MODEL: Optional[Any] = None
_LOCAL_META: Dict[str, Any] = {}

_REG_MODEL: Optional[Any] = None
_REG_META: Dict[str, Any] = {}

class BugReport(BaseModel):
    title: str
    description: str

# -------- Loaders --------
def _load_local_model() -> Tuple[Any, Dict[str, Any]]:
    if not LOCAL_MODEL_PATH.exists():
        raise RuntimeError(f"Local model not found at {LOCAL_MODEL_PATH}. Train first: python src/train.py")
    model = joblib.load(LOCAL_MODEL_PATH)
    meta = {"source": "local", "model_path": str(LOCAL_MODEL_PATH), "stage": None, "version": None, "model_uri": None}
    return model, meta

def _ensure_local_loaded():
    global _LOCAL_MODEL, _LOCAL_META
    if _LOCAL_MODEL is None:
        _LOCAL_MODEL, _LOCAL_META = _load_local_model()

def _ensure_registry_loaded():
    global _REG_MODEL, _REG_META
    if _REG_MODEL is None:
        _REG_MODEL, _REG_META = load_stage_model(name=MLFLOW_MODEL_NAME, stage=MLFLOW_MODEL_STAGE)

def _ensure_default_loaded():
    if PREDICT_MODEL_SOURCE == "registry":
        _ensure_registry_loaded()
    else:
        _ensure_local_loaded()

# -------- Endpoints --------
@app.get("/health")
def health():
    try:
        _ensure_default_loaded()
        meta = (_REG_META if PREDICT_MODEL_SOURCE == "registry" else _LOCAL_META).copy()
        return {"status": "ok", "source_mode": PREDICT_MODEL_SOURCE, **meta}
    except Exception as e:
        return {"status": "degraded", "error": str(e), "source_mode": PREDICT_MODEL_SOURCE}

@app.post("/predict")
def predict(item: BugReport):
    try:
        _ensure_default_loaded()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Model not available: {e}")

    text = f"{item.title or ''} {item.description or ''}".strip()
    model = _REG_MODEL if PREDICT_MODEL_SOURCE == "registry" else _LOCAL_MODEL
    try:
        pred = model.predict([text])[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    return {"severity": str(pred)}

@app.post("/predict-mlflow")
def predict_mlflow(item: BugReport):
    """Force serving from MLflow registry (Production by default)."""
    try:
        _ensure_registry_loaded()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Registry model not available: {e}")

    text = f"{item.title or ''} {item.description or ''}".strip()
    try:
        pred = _REG_MODEL.predict([text])[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    return {"severity": str(pred), "meta": _REG_META}

@app.post("/reload")
def reload_model():
    global _LOCAL_MODEL, _LOCAL_META, _REG_MODEL, _REG_META
    _LOCAL_MODEL = None
    _LOCAL_META = {}
    _REG_MODEL = None
    _REG_META = {}
    try:
        _ensure_default_loaded()
        meta = _REG_META if PREDICT_MODEL_SOURCE == "registry" else _LOCAL_META
        return {"status": "reloaded", **meta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reload failed: {e}")

