# src/batch_score.py
import argparse
import pandas as pd
from src.registry import load_stage_model

def main():
    ap = argparse.ArgumentParser(description="Batch score bug reports via MLflow registry model")
    ap.add_argument("--input", required=True, help="Input CSV with columns: title,description")
    ap.add_argument("--output", required=True, help="Output CSV path")
    ap.add_argument("--stage", default=None, help="Override stage (default env MLFLOW_MODEL_STAGE or Production)")
    ap.add_argument("--name", default=None, help="Override model name (default env MLFLOW_MODEL_NAME)")
    args = ap.parse_args()

    model, meta = load_stage_model(name=args.name, stage=args.stage)

    df = pd.read_csv(args.input)
    required = {"title", "description"}
    if not required.issubset(df.columns):
        raise ValueError(f"Input CSV must contain columns: {sorted(required)}")

    texts = (df["title"].fillna("") + " " + df["description"].fillna("")).str.strip().tolist()
    preds = model.predict(texts)
    df["predicted_severity"] = [str(p) for p in preds]
    df.to_csv(args.output, index=False)
    print(f"[batch_score] Saved predictions to {args.output}")
    print(f"[batch_score] Model: {meta}")

if __name__ == "__main__":
    main()

