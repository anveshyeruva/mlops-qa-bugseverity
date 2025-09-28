# src/train.py
import os
import json
import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

# --- Optional MLflow imports (lazy used) ---
# If mlflow isn't installed, running without --mlflow still works.


def maybe_import_mlflow():
    """
    Import MLflow lazily so the dependency is optional unless --mlflow is used.
    """
    import mlflow
    import mlflow.sklearn
    from mlflow.tracking import MlflowClient
    return mlflow, mlflow.sklearn, MlflowClient


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"title", "description", "severity"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing column(s) in {path}: {sorted(missing)}")

    # Build a single text field
    df["title"] = df["title"].fillna("")
    df["description"] = df["description"].fillna("")
    df["text"] = (df["title"] + " " + df["description"]).str.strip()

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

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(max_features=max_features)),
            ("clf", LinearSVC()),
        ]
    )

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")
    cm = confusion_matrix(y_test, y_pred).tolist()

    metrics = {
        "accuracy": float(acc),
        "f1_weighted": float(f1),
        "confusion_matrix": cm,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "max_features": int(max_features),
    }
    return pipeline, metrics


def save_locally(model, metrics: dict, outdir: Path):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    model_path = outdir / "model.pkl"
    metrics_path = outdir / "metrics.json"

    joblib.dump(model, model_path)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"[local] Saved model → {model_path}")
    print(f"[local] Saved metrics → {metrics_path}")


def parse_args():
    p = argparse.ArgumentParser(description="Bug Severity Classifier Trainer")
    p.add_argument("--data", type=Path, default=Path("data/bugs.csv"),
                   help="Path to CSV with columns: title, description, severity")
    p.add_argument("--outdir", type=Path, default=Path("models"),
                   help="Output directory for local artifacts")
    p.add_argument("--max-features", type=int, default=20_000)
    p.add_argument("--test-size", type=float, default=0.25)
    p.add_argument("--random-state", type=int, default=42)

    # --- MLflow / Registry flags ---
    p.add_argument("--mlflow", action="store_true",
                   help="Log run to MLflow, register model, and move to Staging")
    p.add_argument("--registry-name", default="bug-severity-clf",
                   help="MLflow Registered Model name")

    return p.parse_args()


def main():
    args = parse_args()

    # Load & train
    df = load_data(args.data)
    model, metrics = train_model(
        df,
        max_features=args.max_features,
        random_state=args.random_state,
        test_size=args.test_size,
    )

    # Always save locally (keeps your previous behavior)
    save_locally(model, metrics, args.outdir)

    # --- MLflow logging & registration (only if --mlflow) ---
    if args.mlflow:
        try:
            mlflow, mlflow_sklearn, MlflowClient = maybe_import_mlflow()
        except Exception as e:
            raise SystemExit(
                "You passed --mlflow but MLflow is not available. "
                "Add 'mlflow' to requirements and reinstall."
            ) from e

        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
        mlflow.set_tracking_uri(tracking_uri)

        with mlflow.start_run() as run:
            # Log numeric metrics (ignore non-numeric safely)
            if isinstance(metrics, dict):
                for k, v in metrics.items():
                    try:
                        mlflow.log_metric(k, float(v))
                    except Exception:
                        pass

            # Log model artifact
            mlflow_sklearn.log_model(model, artifact_path="model")
            run_id = run.info.run_id

        # Register & promote to Staging
        model_uri = f"runs:/{run_id}/model"
        reg_name = args.registry_name

        mv = mlflow.register_model(model_uri=model_uri, name=reg_name)
        MlflowClient().transition_model_version_stage(
            name=reg_name,
            version=mv.version,
            stage="Staging",
            archive_existing_versions=False,
        )
        print(f"[mlflow] Registered {reg_name} v{mv.version} → Staging @ {tracking_uri}")


if __name__ == "__main__":
    main()

