# 🐞 QA-Driven MLOps: Bug Severity Classifier

This project demonstrates **QA-first MLOps practices** using a simple bug severity classifier.  
It takes text-based bug reports (title + description) and predicts their severity (`Critical`, `Major`, `Minor`).

The repo currently covers:
- ✅ Training and evaluating a text classifier with **Scikit-learn**
- ✅ Enforcing **quality gates** with unit tests and smoke tests
- ✅ Serving predictions via a **FastAPI** microservice
- ✅ Packaging the service into a **Docker** container

> We’ll add CI/CD and MLflow later and update this README as each step is completed.

---

## 📂 Project Structure

```text
mlops-qa-bugseverity/
├─ data/                 # sample dataset (CSV of bug reports)
├─ models/               # trained artifacts (model + metrics)
├─ src/
│  ├─ train.py           # training script
│  └─ api.py             # FastAPI service
├─ tests/
│  ├─ test_model.py      # unit tests for model + metrics
│  └─ test_api_smoke.py  # smoke tests for /health and /predict
├─ docker/
│  └─ Dockerfile         # container build for API
├─ requirements.txt      # dependencies
├─ .dockerignore
├─ .gitignore
└─ README.md

🚀 Quickstart (Steps 1–2)

1) Setup & Train
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
python src/train.py --data data/bugs.csv --outdir models

2) Test & Serve

Run unit tests:
pytest -q

Start API locally:
uvicorn src.api:app --host 0.0.0.0 --port 8000

Health check:
curl http://127.0.0.1:8000/health

Or run with Docker:
docker build -t mlops-qa-bugseverity:py313 -f docker/Dockerfile .
docker run --rm -p 8000:8000 mlops-qa-bugseverity:py313

✅ API Endpoints

GET /health → { "status": "ok", "model_loaded": true }
POST /predict
 Input:
 { "title": "Save fails", "description": "Crash after boss fight when saving" }

 Output:
 { "severity": "Critical" }

📌 Completed Milestones

 Step 1: Train & unit-test locally
 Step 2: FastAPI service + Docker + API smoke tests