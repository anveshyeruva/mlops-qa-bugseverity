Step 1 — Local training + unit tests + first push
0) Goal
•	stand up a tiny ML project that trains a bug-severity classifier and tests it locally.
________________________________________
1) Create project + virtual environment (Windows + Git Bash)
# pick your folder
mkdir -p /G/Projects/mlops-qa-bugseverity
cd /G/Projects/mlops-qa-bugseverity

# create & activate venv
python -m venv .venv
source .venv/Scripts/activate         # you should see (.venv) in your prompt

# (recommended) upgrade pip inside the venv
python -m pip install --upgrade pip
Troubleshoot
•	If you see “To modify pip, run: …python.exe -m pip…”, run the command exactly as shown (we did above).
•	If activation fails in Git Bash, try:
. .venv/Scripts/activate (note the leading dot + space)
________________________________________
2) Project scaffold (folders + files)
mkdir -p data src tests
.gitignore
__pycache__/
*.pyc
.pytest_cache/
.env
models/
mlruns/
requirements.txt
pandas
scikit-learn
joblib
pytest
fastapi
uvicorn
requests
Troubleshoot
•	If you created files using a heredoc before and got an extra EOF line at the end, delete the literal EOF line from the file.
Check quickly with tail -n 5 requirements.txt.
data/bugs.csv (tiny starter so training works today)
id,title,description,severity
1,Crash on level load,Game crashes when entering level 3,Critical
2,UI misaligned,Inventory button overlaps text on 1080p,Minor
3,Audio stutter,Sound glitches during combat on heavy SFX,Major
4,Save fails on checkpoint,Saving throws error after boss fight,Critical
5,Tooltip overlaps,Tooltip hides item stats in inventory,Minor
6,Low FPS on city map,Frame rate drops below 20 fps in downtown,Major
7,Login timeout,Players stuck on login screen intermittently,Major
8,Tutorial softlock,Player can’t exit tutorial after step 5,Critical
9,HDR washed out,Colors look faded when HDR is enabled,Minor
10,Dialogue skip bug,Skipping dialogue sometimes freezes UI,Major
________________________________________
3) Training code
src/train.py
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
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.25, random_state=42,
        stratify=y if len(set(y)) > 1 else None
    )
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english", max_features=20000)),
        ("clf", LinearSVC())
    ])
    pipe.fit(Xtr, ytr)
    yhat = pipe.predict(Xte)
    metrics = {
        "accuracy": float(accuracy_score(yte, yhat)),
        "f1_macro": float(f1_score(yte, yhat, average="macro")),
        "n_train": int(len(Xtr)),
        "n_test": int(len(Xte)),
        "labels": sorted(list(set(y)))
    }
    return pipe, metrics

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/bugs.csv")
    ap.add_argument("--outdir", default="models")
    a = ap.parse_args()

    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    df = load_data(Path(a.data))
    model, metrics = train(df)

    joblib.dump(model, out / "model.joblib")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print("== Training complete ==")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
________________________________________
4) Unit tests
tests/test_model.py
import json
from pathlib import Path
import joblib, pandas as pd

def test_artifacts_exist():
    assert Path("models/model.joblib").exists(), "Train first: python src/train.py"
    assert Path("models/metrics.json").exists(), "Train first: python src/train.py"

def test_metrics_valid():
    m = json.loads(Path("models/metrics.json").read_text())
    for k in ["accuracy","f1_macro","n_train","n_test","labels"]:
        assert k in m
    assert 0.0 <= m["accuracy"] <= 1.0
    assert isinstance(m["labels"], list) and len(m["labels"]) >= 2

def test_predictions_in_label_set():
    df = pd.read_csv("data/bugs.csv")
    labels = set(df["severity"].unique().tolist())
    model = joblib.load("models/model.joblib")
    preds = model.predict([
        "Game crashes after boss fight when saving",
        "Inventory button overlaps on HDR 4k screen",
        "Frame rate drops on city map with many NPCs"
    ])
    for p in preds:
        assert p in labels
________________________________________
5) Install deps, train, and test
# still inside the activated venv
pip install -r requirements.txt

python src/train.py --data data/bugs.csv --outdir models
# sample output (yours was):
# == Training complete ==
# {
#   "accuracy": 0.6666666666666666,
#   "f1_macro": 0.5555555555555555,
#   "n_train": 7,
#   "n_test": 3,
#   "labels": ["Critical","Major","Minor"]
# }

pytest -q
# expected: all tests pass
Troubleshoot
•	If pytest: command not found in a second terminal → you didn’t activate the venv there.
Fix:
•	cd /G/Projects/mlops-qa-bugseverity
•	source .venv/Scripts/activate
•	# or run without activating:
•	python -m pytest -q
________________________________________
6) Initialize git and first commit
git init
git add .
git commit -m "step1: scaffold, training, unit tests"
________________________________________
7) Push to GitHub (you used GitHub CLI)
7.1 Authenticate once
gh auth login
# choose: GitHub.com → HTTPS → "Login with a web browser" → authorize
7.2 Create remote repo and push in one go
gh repo create mlops-qa-bugseverity --public --source=. --remote=origin --push
If you get “Unable to add remote origin” (you did once), fix like this:
git branch -M main
git remote -v                          # see what's configured
git remote set-url origin https://github.com/anveshyeruva/mlops-qa-bugseverity.git  # or add if missing
git push -u origin main
Verify on GitHub:
https://github.com/anveshyeruva/mlops-qa-bugseverity should show your files.
(Alternative manual way if ever needed)
1.	Create an empty repo on https://github.com/new (no README).
2.	Then:
git remote add origin https://github.com/anveshyeruva/mlops-qa-bugseverity.git
git branch -M main
git push -u origin main
________________________________________
8) What to capture for notes
•	The printed metrics from training (models/metrics.json).
•	A screenshot of pytest -q passing.
•	A screenshot of your GitHub repo after push.

