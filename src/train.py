# src/train.py
import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


def maybe_import_mlflow():
    """
    Import MLflow lazily so the dependency is optional unless --mlflow is used.
    """
    import mlflow
    from mlflow import sklearn as mlflow_sklearn
    return mlflow, mlflow_sklearn


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"title", "description", "severity"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing column(s) in {path}: {sorted(missing)}")

    # Build a single text field the model expects
    df["title"] = df["title"].fillna("")
    df["description"] = df["description"].fillna("")
    df["text"] = (df["title"] + " " + df["description"]).str.strip()

    # Keep only what we need
    df = df[["text", "severity"]].dropna()
    if df.empty:
        raise ValueError("No rows to train on after cleaning.")
    return df


def train_model(
    df: pd.DataFrame,
    *,
    max_features: int = 20_000,
    random_state: int = 42,
    test_size: float = 0.25,
):
    X, y = df["text"].values, df["severity"].values

    # Deterministic label order for metrics/confusion matrix
    label_list = sorted(pd.unique(y).tolist())

    # Stratify only if more than one class present
    stratify = y if len(label_list) > 1 else None

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )

    pipe = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english", max_features=max_features)),
            ("clf", LinearSVC()),
        ]
    )
    pipe.fit(Xtr, ytr)

    yhat = pipe.predict(Xte)

    metrics = {
        "accuracy": float(accuracy_score(yte, yhat)),
        "f1_macro": float(f1_score(yte, yhat, average="macro")),
        "n_train": int(len(Xtr)),
        "n_test": int(len(Xte)),
        "labels": label_list,
    }

    cm = confusion_matrix(yte, yhat, labels=label_list)
    return pipe, metrics, (label_list, cm.tolist())


def main():
    ap = argparse.ArgumentParser(description="Train bug severity classifier & save artifacts.")
    ap.add_argument("--data", default="data/bugs.csv", help="Path to CSV with title, description, severity")
    ap.add_argument("--outdir", default="models", help="Output dir for model + metrics")
    # MLflow options
    ap.add_argument("--mlflow", action="store_true", help="Enable MLflow tracking/logging")
    ap.add_argument("--experiment", default="bug-severity", help="MLflow experiment name")
    ap.add_argument("--run-name", default=None, help="MLflow run name")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = load_data(Path(args.data))
    model, metrics, (labels, cm) = train_model(df)

    # Save artifacts locally (always)
    model_path = outdir / "model.joblib"
    metrics_path = outdir / "metrics.json"
    cm_path = outdir / "confusion_matrix.json"

    joblib.dump(model, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2))
    cm_payload = {"labels": labels, "confusion_matrix": cm}
    cm_path.write_text(json.dumps(cm_payload, indent=2))

    print("== Training complete ==")
    print(json.dumps(metrics, indent=2))

    # Optional MLflow logging (signature-only; no input_example to avoid validation issues)
    if args.mlflow:
        mlflow, mlflow_sklearn = maybe_import_mlflow()
        mlflow.set_experiment(args.experiment)
        with mlflow.start_run(run_name=args.run_name):
            # Params
            mlflow.log_param("model", "LinearSVC")
            mlflow.log_param("tfidf_max_features", 20_000)
            mlflow.log_param("test_size", 0.25)
            mlflow.log_param("random_state", 42)

            # Metrics
            mlflow.log_metric("accuracy", metrics["accuracy"])
            mlflow.log_metric("f1_macro", metrics["f1_macro"])
            mlflow.log_metric("n_train", metrics["n_train"])
            mlflow.log_metric("n_test", metrics["n_test"])

            # Artifacts
            mlflow.log_artifact(str(metrics_path), artifact_path="artifacts")
            mlflow.log_artifact(str(cm_path), artifact_path="artifacts")

            # Model with explicit signature (string -> string)
            from mlflow.models import ModelSignature
            from mlflow.types.schema import Schema, ColSpec

            signature = ModelSignature(
                inputs=Schema([ColSpec("string")]),
                outputs=Schema([ColSpec("string")]),
            )

            mlflow_sklearn.log_model(
                sk_model=model,
                name="bug-severity-model",
                signature=signature,
            )

            print("[mlflow] logged run:", mlflow.active_run().info.run_id)


if __name__ == "__main__":
    main()

