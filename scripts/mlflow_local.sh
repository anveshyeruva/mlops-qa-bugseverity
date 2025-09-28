#!/usr/bin/env bash
set -euo pipefail

# Simple local registry using SQLite (works on dev laptops and CI)
export MLFLOW_BACKEND_URI=${MLFLOW_BACKEND_URI:-sqlite:////tmp/mlflow.db}
export MLFLOW_ARTIFACT_ROOT=${MLFLOW_ARTIFACT_ROOT:-file:/tmp/mlruns}

# Kill any previous
pkill -f "mlflow server" || true

# Start server on 5000
mlflow server \
  --backend-store-uri "$MLFLOW_BACKEND_URI" \
  --default-artifact-root "$MLFLOW_ARTIFACT_ROOT" \
  --host 127.0.0.1 --port 5000 >/tmp/mlflow.log 2>&1 &

# Wait for port
python - <<'PY'
import socket, time
for _ in range(60):
    s=socket.socket(); 
    try:
        s.connect(("127.0.0.1",5000)); s.close(); print("MLflow up"); break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("MLflow did not start")
PY
echo "MLflow web UI: http://127.0.0.1:5000"

