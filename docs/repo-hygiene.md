# Repo Hygiene Verification

This document is a checklist to verify `.gitattributes` and `.gitignore` are working correctly. 

It also records actual verification results from Step 1–4.

1. Source Code & Markdown
Should be stored as text with diffs.

```bash
git check-attr text -- src/train.py
git check-attr text -- docs/step1.md
git check-attr text -- docs/step2.md
git check-attr text -- docs/step3.md
git check-attr text -- docs/step4.md

Expected: text: set
Result (Step 1–4): All returned text: set

2. Data Files (CSV)
Should allow diffs.

git check-attr diff -- data/bugs.csv

Expected: diff: set
Result (Step 1): data/bugs.csv: diff: set

3. Models (joblib / pickle)
Should be binary.

git check-attr binary -- models/model.joblib

Expected: binary: set
Result (Step 2, Step 4): models/model.joblib: binary: set

4. Images
Binary formats (PNG, JPG) should be binary.

git check-attr binary -- docs/images/step4/bug_severity_runs.png
git check-attr binary -- docs/images/step4/model_metrics.png

Expected: binary: set
Result (Step 4):
- bug_severity_runs.png: text: unset (correct, handled as binary)
- model_metrics.png: binary: set

SVG (vector) should be text.

git check-attr text -- docs/images/diagram.svg

Expected: text: set
Result (Step 4): No SVG tested yet.

5. MLflow Runs
Should be excluded from diffs & stats.
Configured in .gitattributes and .gitignore.

git status

Expected: mlruns/ ignored in commits.
Result (Step 4): Confirmed mlruns/ was not staged for commit. GitHub linguist stats unaffected.

6. Extra OS/Editor Files
.DS_Store, .venv/, .venv311/, and __pycache__/ must be ignored.

git status

Expected: They appear only as untracked (if present locally).
Result (Step 3–4): .DS_Store appeared but was ignored after adding to .gitignore
