# Step 3: CI/CD Pipeline with Regression Gates + API Smoke Tests

In this step, we integrated a **Continuous Integration (CI)** pipeline using **GitHub Actions**.  
The pipeline ensures that every push automatically triggers model training, regression validation, API smoke testing, and Docker build.  

---

## Initial Setup

Created the workflow folder and file:

```bash
mkdir -p .github/workflows
vi .github/workflows/ci.yml

Initial Workflow Content
name: Step 3: CI pipeline + QA regression gate + API smoke in CI

on:
  push:
    branches: [ "main" ]
  pull_request:

jobs:
  test-train-serve:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Unit tests (fast)
        run: pytest -q -m "not integration"

      - name: Train model
        run: python src/train.py --data data/bugs.csv --outdir models

      - name: QA gate
        run: python qa_gate.py

      - name: Start API
        run: |
          nohup uvicorn src.api:app --host 127.0.0.1 --port 8000 > uvicorn.log 2>&1 &
          sleep 3

      - name: Wait for /health
        run: |
          for i in {1..20}; do
            curl -s http://127.0.0.1:8000/health | grep -q '"model_loaded": true' && exit 0
            sleep 1
          done
          cat uvicorn.log
          exit 1

      - name: Integration tests
        run: pytest -q -m "integration"

Issues and Fixes
1. No tests collected

Error:

pytest -m "not integration"
collected 0 items


Cause: all existing tests were marked as integration.

Fix:

Added pytest.ini:

[pytest]
markers =
    integration: tests that require trained artifacts or a running API


Added tests/test_sanity.py:

from pathlib import Path

def test_repo_sanity():
    assert Path("src/train.py").exists()
    assert Path("src/api.py").exists()

2. API health checks failed (model_loaded=false)

CI logs showed:

{"status":"ok","model_loaded":false}


Cause: FastAPI service couldn’t load the model in CI.

Fix: Updated src/api.py to resolve absolute model path and add lazy loading:

from pathlib import Path
import joblib, os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Bug Severity API", version="0.1.0")

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
            print("[api] model loaded ok")
    except Exception as e:
        print(f"[api] model load failed: {e}")
    return model is not None

@app.on_event("startup")
def load_model_on_startup():
    print(f"[api] startup cwd={os.getcwd()}")
    print(f"[api] expected model path={MODEL_PATH}")
    ensure_model_loaded()

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": ensure_model_loaded()}

@app.post("/predict")
def predict(item: BugReport):
    if not ensure_model_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    text = f"{item.title} {item.description}".strip()
    return {"severity": model.predict([text])[0]}

3. Duplicate run: keys in workflow

Error:

Invalid workflow file: 'run' is already defined


Cause: mistakenly had two run: blocks under Start API.

Fix: merged into a single block:

- name: Start API (background)
  run: |
    echo "PWD=$(pwd)"
    ls -l models || true
    test -f models/model.joblib || (echo "model missing"; exit 1)
    nohup uvicorn src.api:app --host 127.0.0.1 --port 8000 > uvicorn.log 2>&1 &
    sleep 3

4. Health check grep mismatch

CI logs showed:

Health: {"status":"ok","model_loaded":true}


But our grep expected:

"model_loaded": true


Fix: changed to whitespace-tolerant regex:

- name: Wait for /health
  run: |
    for i in {1..20}; do
      BODY=$(curl -s http://127.0.0.1:8000/health || true)
      echo "Health: $BODY"
      echo "$BODY" | grep -E -q '"model_loaded":[[:space:]]*true' && exit 0
      sleep 1
    done
    cat uvicorn.log
    exit 1

Final Outcome

Sanity tests run instantly.

Model training and regression gates run on every push.

FastAPI service starts inside CI and passes /health checks.

Smoke tests confirm /predict works correctly.

Docker image builds successfully.

This completed Step 3 milestone, tagged as v0.2.
