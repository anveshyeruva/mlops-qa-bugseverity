Step 2 — FastAPI service + API smoke tests + Docker
0) Goal
•	Serve the trained model via an HTTP API.
•	Add smoke tests that hit the running API.
•	Containerize the service with Docker so it runs anywhere.
Prereq: Step 1 is done and you have a trained model in models/.
________________________________________
1) Add/Update files
1.1 src/api.py (FastAPI app)
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
1.2 tests/test_api_smoke.py (end-to-end smoke test)
# tests/test_api_smoke.py
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
    labels = None
    metrics_path = Path("models/metrics.json")
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text())
        labels = set(metrics.get("labels", []))
    else:
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
Note: This test expects the API to be running (locally or in Docker). It waits up to 20 seconds for /health to report model_loaded=true.
1.3 .dockerignore (keeps the image lean)
.venv
__pycache__
*.pyc
.pytest_cache
.git
.gitignore
mlruns
data
1.4 docker/Dockerfile (Python 3.13 to match your local)
# docker/Dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY src/ src/
COPY models/ models/

EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
________________________________________
2) Run the API locally (no Docker)
Make sure you have a model:
python src/train.py --data data/bugs.csv --outdir models
Start the API (Terminal #1, keep it open):
uvicorn src.api:app --host 127.0.0.1 --port 8000
Smoke test (Terminal #2):
BASE_URL=http://127.0.0.1:8000 pytest -q tests/test_api_smoke.py
Manual curl checks (optional):
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" \
  -d '{"title":"Save fails","description":"Crash after boss fight when saving"}'
Expected: /health shows model_loaded: true; /predict returns a label like "Critical".
________________________________________
3) Run the API in Docker
Build:
docker build -t mlops-qa-bugseverity:py313 -f docker/Dockerfile .
Run:
docker run --rm -p 8000:8000 mlops-qa-bugseverity:py313
Smoke test from host (new terminal):
BASE_URL=http://127.0.0.1:8000 pytest -q tests/test_api_smoke.py
________________________________________
4) Troubleshooting (the exact issues you hit)
•	Smoke test failed: “connection refused”
Cause: API wasn’t running.
Fix: Start Uvicorn (or Docker container) first, then re-run the smoke test.
•	pytest: command not found (second terminal)
Cause: The venv wasn’t activated in that terminal.
Fix:
•	cd /G/Projects/mlops-qa-bugseverity
•	source .venv/Scripts/activate
•	# or use: python -m pytest -q tests/test_api_smoke.py
•	Windows firewall pop-up when starting Uvicorn:
Allow access (private networks) so localhost/127.0.0.1 works.
•	Port already in use
Use another port:
•	uvicorn src.api:app --host 127.0.0.1 --port 8001
•	BASE_URL=http://127.0.0.1:8001 pytest -q tests/test_api_smoke.py
•	docker: command not found
Install Docker Desktop for Windows (AMD64) and restart.
•	Model not loaded (503)
Train first:
•	python src/train.py --data data/bugs.csv --outdir models
________________________________________
5) Commit & push (Step 2 changes)
git add src/api.py tests/test_api_smoke.py docker/Dockerfile .dockerignore requirements.txt
git commit -m "step2: FastAPI service, API smoke tests, Docker image"
git push origin main
If you hadn’t added the README earlier, include it too:
git add README.md
git commit -m "docs: README for steps 1–2"
git push
________________________________________
6) (Optional) Tag + Release for Step 1–2 completion
You chose to tag both steps as v0.1.
git tag -a v0.1 -m "Step 1–2 complete: training, tests, FastAPI, Docker, smoke tests"
git push origin v0.1
Then on GitHub → Releases → Draft a new release:
•	Tag: v0.1
•	Title: v0.1 – Training, FastAPI, Docker, Tests
•	Notes: short list of what’s included + mention Milestone Step 1–2 (v0.1)
________________________________________
7) What to save as proof (for your notes/paper)
•	Screenshot: uvicorn startup log
•	Screenshot: curl /health and /predict responses
•	Terminal output: pytest -q tests/test_api_smoke.py (2 passed)
•	Docker build and run logs
•	GitHub release page for v0.1

