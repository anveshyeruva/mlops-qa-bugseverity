# 🛠️ Step 2 Troubleshooting Log

This file documents all issues encountered while setting up **FastAPI service, smoke tests, and Docker** in Step 2.

---

## ❌ Issue 1: Smoke tests failed

**Error:**
AssertionError: API /health did not become ready with model_loaded=true

ruby
Copy code

**Cause:** API was not running when tests were executed.  

**Fix:**  
- Launched the API first:
```bash
uvicorn src.api:app --reload
Then re-ran smoke tests:

bash
Copy code
BASE_URL=http://127.0.0.1:8000 pytest -q tests/test_api_smoke.py
❌ Issue 2: pytest not found in second terminal
Error:

bash
Copy code
bash: pytest: command not found
Cause: The virtual environment was not activated in the second terminal.

Fix: Activated venv again:

bash
Copy code
source .venv/bin/activate   # macOS/Linux
source .venv/Scripts/activate   # Windows Git Bash
✅ Final Resolution
/health returned 200 with "model_loaded": true.

/predict endpoint passed smoke tests.

Docker installed and verified with:

bash
Copy code
docker --version
🎉 Step 2 complete and project ready for CI/CD integration.
