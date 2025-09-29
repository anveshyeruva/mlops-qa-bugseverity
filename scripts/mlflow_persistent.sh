#!/usr/bin/env bash
set -euo pipefail

: "${MLFLOW_BACKEND_URI:?set MLFLOW_BACKEND_URI (e.g., postgresql+psycopg2://user:pass@host:5432/mlflow)}"
: "${MLFLOW_ARTIFACT_ROOT:?set MLFLOW_ARTIFACT_ROOT (e.g., s3://my-bucket/mlflow-artifacts)}"

MLFLOW_HOST="${MLFLOW_HOST:-127.0.0.1}"
MLFLOW_PORT="${MLFLOW_PORT:-5000}"

echo "[mlflow] backend: $MLFLOW_BACKEND_URI"
echo "[mlflow] artifacts: $MLFLOW_ARTIFACT_ROOT"
echo "[mlflow] http: http://$MLFLOW_HOST:$MLFLOW_PORT"

exec mlflow server \
  --backend-store-uri "$MLFLOW_BACKEND_URI" \
  --artifacts-destination "$MLFLOW_ARTIFACT_ROOT" \
  --host "$MLFLOW_HOST" \
  --port "$MLFLOW_PORT"

