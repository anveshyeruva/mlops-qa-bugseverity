# src/registry.py
from __future__ import annotations
import os
from typing import Any, Dict, Tuple

import mlflow
from mlflow.tracking import MlflowClient


def get_tracking_uri() -> str:
    uri = os.getenv("MLFLOW_TRACKING_URI")
    if not uri:
        raise RuntimeError("MLFLOW_TRACKING_URI is not set")
    return uri


def get_model_name() -> str:
    return os.getenv("MLFLOW_MODEL_NAME", "bug-severity-clf")


def get_model_stage() -> str:
    return os.getenv("MLFLOW_MODEL_STAGE", "Production")


def load_stage_model(name: str | None = None, stage: str | None = None) -> Tuple[Any, Dict[str, Any]]:
    """
    Load a model by stage from the MLflow Model Registry and return (model, meta).
    """
    name = name or get_model_name()
    stage = stage or get_model_stage()

    tracking_uri = get_tracking_uri()
    mlflow.set_tracking_uri(tracking_uri)

    model_uri = f"models:/{name}/{stage}"
    model = mlflow.sklearn.load_model(model_uri)  # sklearn pipeline expected

    version = None
    client = MlflowClient()
    for mv in client.search_model_versions(f"name='{name}'"):
        if mv.current_stage == stage:
            try:
                version = int(mv.version)
            except Exception:
                version = str(mv.version)

    meta = {
        "tracking_uri": tracking_uri,
        "model_uri": model_uri,
        "name": name,
        "stage": stage,
        "version": version,
    }
    return model, meta

