import argparse, json
from pathlib import Path
import joblib, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, f1_score

def load_data(p: Path):
    df = pd.read_csv(p)
    for col in ["title", "description", "severity"]:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
    df["text"] = (df["title"].fillna("") + " " + df["description"].fillna("")).str.strip()
    return df[["text","severity"]].dropna()

def train(df):
    X, y = df["text"].values, df["severity"].values
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y if len(set(y))>1 else None)
    pipe = Pipeline([("tfidf", TfidfVectorizer(lowercase=True, stop_words="english", max_features=20000)),
                     ("clf", LinearSVC())])
    pipe.fit(Xtr, ytr)
    yhat = pipe.predict(Xte)
    metrics = {"accuracy": float(accuracy_score(yte, yhat)),
               "f1_macro": float(f1_score(yte, yhat, average="macro")),
               "n_train": int(len(Xtr)), "n_test": int(len(Xte)),
               "labels": sorted(list(set(y)))}
    return pipe, metrics

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/bugs.csv")
    ap.add_argument("--outdir", default="models")
    a = ap.parse_args()
    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    model, metrics = train(load_data(Path(a.data)))
    joblib.dump(model, out / "model.joblib")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print("== Training complete =="); print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()

