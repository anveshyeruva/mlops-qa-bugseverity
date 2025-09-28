# Step 5 — MLflow Model Registry & Promotion

## What we do
- Log training runs to MLflow
- Register the trained model as `bug-severity-clf`
- Promote to **Staging** (automatic) and then **Production** (CI)

## Local quickstart
```bash
# 1) start registry locally
scripts/mlflow_local.sh
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000

# 2) train + register
python src/train.py --data data/bugs.csv --outdir models --mlflow --registry-name bug-severity-clf

# 3) open UI
open http://127.0.0.1:5000

