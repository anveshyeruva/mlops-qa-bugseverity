# 🛠️ Step 3 Troubleshooting Log

This file documents all issues encountered while setting up **CI/CD with GitHub Actions** in Step 3, along with raw error outputs and the fixes applied.  

---

## ❌ Issue 1: No tests collected

**Error seen in CI logs:**
pytest -m "not integration"
collected 0 items

markdown
Copy code

**Cause:** all tests were marked as `integration`, so nothing was available for `-m "not integration"`.  

**Fix:**
- Registered `integration` marker in `pytest.ini`.
- Added `tests/test_sanity.py` for lightweight fast tests.

---

## ❌ Issue 2: API health checks failing

**Error seen in CI logs:**
Health: {"status":"ok","model_loaded":false}
API not ready

markdown
Copy code

**Cause:** FastAPI process could not find or load `models/model.joblib` in CI.  

**Fix:**
- Updated `src/api.py` to:
  - Resolve **absolute model path**.
  - Add **lazy-loading** in `/health`.
  - Log startup details (`cwd`, expected model path, load success/failure).

---

## ❌ Issue 3: Duplicate `run:` keys in workflow

**Error when pushing workflow:**
Invalid workflow file
(Line: 46, Col: 9): 'run' is already defined

yaml
Copy code

**Cause:** YAML step had two `run:` blocks under `Start API`.  

**Fix:** merged into a single `run:` block.

---

## ❌ Issue 4: Health check grep mismatch

**Error seen in CI logs:**
Health: {"status":"ok","model_loaded":true}
API not ready

swift
Copy code

**Cause:** JSON output had no space (`"model_loaded":true`) but grep expected `"model_loaded": true`.  

**Fix:** changed grep to allow optional whitespace:

```bash
grep -E '"model_loaded":[[:space:]]*true'
✅ Final Resolution
After applying all fixes:

/health returned {"status":"ok","model_loaded":true} and matched correctly.

API logs confirmed [api] model loaded ok.

CI pipeline passed end-to-end with green checks.

🎉 Troubleshooting complete.
