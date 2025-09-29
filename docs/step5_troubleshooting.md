Step 5 — Troubleshooting (Model Registry & Deployment)

This page documents common issues encountered during Step 5 and their fixes.

1. QA Gate fails with label mismatch

Error

[qa_gate] ERROR: New labels set () does not cover baseline {'Critical', 'Major', 'Minor'}


Cause

metrics.json didn’t contain any labels, or

the training data used different severity names (low/medium/high).

Fix

Ensure train.py writes labels into metrics.json.

Normalize severity values in load_data() to Critical / Major / Minor.

2. QA Gate fails with accuracy drop

Error

[qa_gate] FAIL: accuracy dropped beyond tolerance (0.6667 -> 0.5500)


Cause

Model underperformed compared to baseline.

Dataset too small or changed distribution.

Fix

Recheck preprocessing and label mapping.

Increase training data.

Adjust TOLERANCE in scripts/qa_gate.py if drop is acceptable (not recommended unless intentional).

3. MLflow server not starting (local or CI)

Error

MLflow did not start


Cause

Port 5000 already in use.

SQLite lock file left behind.

MLflow not installed in environment.

Fix

Kill old MLflow process:

pkill -f "mlflow server"


Clear old artifacts:

rm -rf /tmp/mlruns /tmp/mlflow.db


Reinstall:

pip install mlflow

4. No Staging versions found to promote

Error

No Staging versions found to promote.


Cause

Training ran without --mlflow.

Model wasn’t logged correctly.

Fix

Run training with:

python src/train.py --data data/bugs.csv --outdir models --mlflow --registry-name bug-severity-clf

5. Registry smoke test fails (no Production version)

Error

AssertionError: No Production version in registry


Cause

Promotion step didn’t run.

MLflow connection issue.

Fix

Check CI logs for promotion step.

Verify MLFLOW_TRACKING_URI env is set.

Manually promote via MLflow UI as a fallback.

6. API smoke test fails (/predict not working)

Symptoms

API starts but health check never returns ok.

/predict returns error 422.

Cause

Missing model file (model.pkl or model.joblib).

Schema mismatch in request payload.

Fix

Verify train.py saves model in models/.

Update payload example in CI if input schema changes.

Check uvicorn.log artifact for full error trace.

7. Retagging issues with Git

Symptoms

Tag exists but doesn’t include Step 5 changes.

Error deleting tag:

fatal: tag shorthand without <tag>


Fix

Correct commands:

git tag -d v0.4.0
git push origin --delete v0.4.0
git checkout main
git merge feat/step5-mlflow-registry
git push origin main
git tag -a v0.4.0 -m "Model Registry & Deployment (Step 5)"
git push origin v0.4.0

8. CI job times out

Cause

MLflow server or API takes longer than expected to start.

Insufficient sleep/retry loop.

Fix

Increase sleep/retries in CI steps.

Check logs (mlflow.log, uvicorn.log) via artifacts.
