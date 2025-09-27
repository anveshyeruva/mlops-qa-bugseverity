# Troubleshooting Notes — Step 4 (MLflow Integration)

This file documents the issues encountered while integrating **MLflow experiment tracking** in Step 4, and how we resolved them.

---

## 1. Experiment Creation Warning

**Error/Warning:**
Experiment with name 'bug-severity' does not exist. Creating a new experiment.


**Cause:**  
The first time `mlflow.start_run()` is called, MLflow automatically creates the experiment if it doesn’t exist.

**Fix:**  
No action needed. This is expected behavior. Future runs use the same experiment.

---

## 2. Deprecation Warnings

**Warning:**


mlflow.models.model: artifact_path is deprecated. Please use name instead.


**Cause:**  
Newer versions of MLflow prefer `name` over `artifact_path`.

**Fix:**  
Updated our `train.py` to use:
```python
mlflow.sklearn.log_model(model, artifact_path="model", input_example=input_example)


This is still valid, but will be migrated to the name parameter in the future if needed.

3. Input Example Validation Error

Error:

'int' object has no attribute 'lower'


Cause:
MLflow tried to validate the input example using the raw DataFrame, which contained non-text fields.

Fix:
We manually created an input_example dictionary with "title" and "description" fields, matching the model’s expected inputs.

input_example = {
    "title": "Save fails on checkpoint",
    "description": "Crash after boss fight when saving progress"
}
mlflow.sklearn.log_model(model, artifact_path="model", input_example=input_example)

4. Launching MLflow UI

Issue:
MLflow UI did not display experiments immediately.

Fix:
Run the UI with the correct backend store:

mlflow ui --backend-store-uri ./mlruns -p 5000


Then visit: http://127.0.0.1:5000
.

5. Git Integration Notes

Created a new feature branch: feature/step4-mlflow

Opened a PR via gh pr create

Squash-merged into main

Tagged release as v0.3

Linked to Milestone 3


---

Next step:  

1. Create the file:
   ```bash
   nano docs/troubleshooting_step4.md


(or use your editor, paste the above content, save)

Stage, commit, and push:

git add docs/troubleshooting_step4.md
git commit -m "docs: add troubleshooting notes for step4 (MLflow integration)"
git push origin main
