# 🛠️ Step 1 Troubleshooting Log

This file documents all issues encountered while setting up **project initialization and environment setup** in Step 1.

---

## ❌ Issue 1: `gh` command not found

**Error:**
bash: gh: command not found

ruby
Copy code

**Cause:** GitHub CLI was not installed.  

**Fix:** Installed GitHub CLI and confirmed with:
```bash
gh --version
❌ Issue 2: pip upgrade error
Error:

vbnet
Copy code
ERROR: To modify pip, please run the following command:
G:\Projects\mlops-qa-bugseverity\.venv\Scripts\python.exe -m pip install --upgrade pip
Cause: pip install --upgrade pip was run directly instead of using the venv’s Python.

Fix:

bash
Copy code
python -m pip install --upgrade pip
❌ Issue 3: requirements.txt contained EOF
Error:

yaml
Copy code
ERROR: No matching distribution found for EOF
Cause: Accidental EOF line was left in requirements.txt.

Fix: Removed the EOF line from the file.

✅ Final Resolution
Virtual environment activated successfully.

Dependencies installed from requirements.txt.

Training script executed without issues:

bash
Copy code
python src/train.py --data data/bugs.csv --outdir models
🎉 Step 1 complete and tagged as v0.1.
