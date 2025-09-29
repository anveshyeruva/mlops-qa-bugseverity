param(
  [string]$HostIp = $env:MLFLOW_HOST  ? $env:MLFLOW_HOST  : "127.0.0.1",
  [string]$Port   = $env:MLFLOW_PORT  ? $env:MLFLOW_PORT  : "5000"
)

if (-not $env:MLFLOW_BACKEND_URI) {
  throw "Set MLFLOW_BACKEND_URI (e.g., postgresql+psycopg2://user:pass@host:5432/mlflow)"
}
if (-not $env:MLFLOW_ARTIFACT_ROOT) {
  throw "Set MLFLOW_ARTIFACT_ROOT (e.g., s3://my-bucket/mlflow-artifacts)"
}

Write-Host "[mlflow] backend: $($env:MLFLOW_BACKEND_URI)"
Write-Host "[mlflow] artifacts: $($env:MLFLOW_ARTIFACT_ROOT)"
Write-Host "[mlflow] http: http://$HostIp:$Port"

python -m mlflow server `
  --backend-store-uri "$($env:MLFLOW_BACKEND_URI)" `
  --artifacts-destination "$($env:MLFLOW_ARTIFACT_ROOT)" `
  --host $HostIp `
  --port $Port

