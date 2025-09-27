import os
import time
import json
from pathlib import Path
import requests
import pandas as pd

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

def wait_for_health(timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=3)
            if r.status_code == 200 and r.json().get("model_loaded") is True:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

def test_health_ok():
    assert wait_for_health(20), "API /health did not become ready with model_loaded=true"

def test_predict_labels_valid():
    # allowed labels from our data or metrics.json
    labels = None
    metrics_path = Path("models/metrics.json")
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text())
        labels = set(metrics.get("labels", []))
    else:
        # fallback: read from data (dev convenience)
        df = pd.read_csv("data/bugs.csv")
        labels = set(df["severity"].unique().tolist())

    payload = {
        "title": "Save fails on checkpoint",
        "description": "Crash after boss fight when saving progress"
    }
    r = requests.post(f"{BASE_URL}/predict", json=payload, timeout=5)
    assert r.status_code == 200, f"/predict failed: {r.status_code} {r.text}"
    out = r.json()
    assert "severity" in out, f"Missing 'severity' in response: {out}"
    assert out["severity"] in labels, f"Got unexpected label {out['severity']}, allowed={labels}"

