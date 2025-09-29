Step 5 — MLflow Model Registry & Deployment (v0.4)
Goals

Log training runs to MLflow.

Register the trained model as bug-severity-clf.

Auto-promote Staging → Production in CI after sanity checks.

Keep local artifacts for dev; use an ephemeral registry in CI.

Prerequisites

mlflow added to requirements.txt.

Updated src/train.py supports:

--mlflow and --registry-name

saving models/model.pkl and models/metrics.json

writing labels into metrics for QA (e.g., ["Critical","Major","Minor"])

CI workflow updated with the registry-smoke job.

Local workflow (quickstart)
# 1) Start a local MLflow server (SQLite + local files)
nohup mlflow server \
  --backend-store-uri sqlite:////tmp/mlflow.db \
  --default-artifact-root file:/tmp/mlruns \
  --host 127.0.0.1 --port 5000 > /tmp/mlflow.log 2>&1 &

# 2) Point training to that server
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000

# 3) Train + log + register (auto → Staging)
python src/train.py --data data/bugs.csv --outdir models --mlflow --registry-name bug-severity-clf

# 4) Open the UI
open http://127.0.0.1:5000

CI workflow (what the pipeline does)

Job test-train-serve

installs deps → runs unit tests (fast)

trains locally and saves models/

QA gate (scripts/qa_gate.py): compares models/metrics.json to qa/baseline_metrics.json

checks label coverage and accuracy tolerance

boots API and smoke-tests /health and /predict

Job registry-smoke

starts ephemeral MLflow (SQLite + file artifacts)

trains with --mlflow → registers model → promotes latest Staging → Production

verifies at least one Production version exists

Note: The registry in CI is ephemeral (per-run). For a persistent registry, move to Postgres + S3 and store URIs/creds in GitHub Actions secrets (Milestone 5).

Label normalization (important)

To keep QA consistent across datasets, we normalize severity to a fixed set:

Input examples: low/medium/high, minor/major/critical

Normalized → Minor, Major, Critical

This happens in src/train.py inside load_data(). The metrics file must include:

"labels": ["Critical", "Major", "Minor"]


The QA gate checks that baseline labels are covered by new labels, preventing accidental class drift.

Promotion policy (current)

CI auto-promotes latest Staging → Production if:

QA gate passes (accuracy within tolerance; labels cover baseline).

Manual overrides can be done via the MLflow UI when needed.

Artifacts produced

Local:

models/model.pkl, models/metrics.json

MLflow (when --mlflow):

Run with metrics + artifacts under the active tracking URI

Registered model: bug-severity-clf with versions & stages

Common commands

Train (local only)

python src/train.py --data data/bugs.csv --outdir models


Train + register (local MLflow)

export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
python src/train.py --data data/bugs.csv --outdir models --mlflow --registry-name bug-severity-clf


QA gate (local check)

python scripts/qa_gate.py

Troubleshooting

[qa_gate] ERROR: New labels set () does not cover baseline {...}
Ensure metrics.json contains a labels array and that load_data() normalizes severities to Critical/Major/Minor.

MLflow server not starting (CI/local)
Inspect mlflow.log. For local dev, remove /tmp/mlflow.db and /tmp/mlruns and retry.

No Staging versions to promote
Make sure training ran with --mlflow and the run logged a model.

Next steps (Milestone 5 preview)

Switch to persistent registry (Postgres + S3) with GitHub Secrets.

Add model signature and pip_requirements to logged models.

Add API route /predict-mlflow to load the Production model from the registry.

Add a small batch scoring script that reads the Production model from MLflow.

End of Step 5.
