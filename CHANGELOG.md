# Changelog

All notable changes to this project will be documented in this file.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and tags follow [Semantic Versioning](https://semver.org/).

---

## [v0.3.2] - 2025-09-28
### Fixed
- Align Docker base image to Python 3.11 (matches GitHub Actions CI)
- Cleaned `.dockerignore` to exclude unnecessary files (`data/`, `models/`)
- Updated `docker/Dockerfile` to ensure empty directories (`data/`, `models/`) exist inside container
- Pinned dependencies in `requirements.txt` for reproducible builds across macOS and Windows

### Notes
This patch ensures that Docker builds succeed consistently in CI and local environments, and guarantees reproducible runs for future publication and paper-ready workflows.

---

## [v0.3.1] - 2025-09-27
### Repo Hygiene & Documentation
- Added `docs/repo-hygiene.md` with verification checklist and actual outputs for Steps 1–4.
- Updated `.gitattributes` to enforce correct handling of:
  - Source code & markdown → stored as text
  - CSV data → diffable
  - Models (`.joblib`, `.pkl`) → binary
  - Images (PNG/JPG) → binary
  - SVGs → text
- Confirmed MLflow runs (`mlruns/`) excluded from versioning & stats.
- Aligned hygiene with publication-ready standards.

Tagged as `v0.3.1` (patch release) linked to Milestone 3.

---

## [v0.3] - Step 4: MLflow Experiment Tracking
- Integrated **MLflow** for experiment tracking.
- Added CLI flag `--mlflow` to enable/disable logging.
- Model, metrics, and confusion matrix are now logged as artifacts.
- Added `docs/step4.md` for documentation.
- Added `docs/troubleshooting_step4.md` for troubleshooting notes.

---

## [v0.2] - 2025-09-27
### Added
- CI/CD pipeline with GitHub Actions (`.github/workflows/ci.yml`).
- Automated smoke tests for API endpoints (`/health`, `/predict`).
- Documentation for Step 3 (`docs/step3.md`).
- Troubleshooting log for Step 3 (`docs/troubleshooting_step3.md`).

### Fixed
- CI failing on `/health` check due to timing issues → resolved with retry logic.
- macOS permission error with `~/.config/gh` fixed using `chown`.

### References
- Milestone: [Milestone 2](https://github.com/anveshyeruva/mlops-qa-bugseverity/milestone/2)
- Release: [Release v0.2](https://github.com/anveshyeruva/mlops-qa-bugseverity/releases/tag/v0.2)

---

## [v0.1] - 2025-09-26
### Added
- Initial project setup with directories: `src/`, `data/`, `models/`, `tests/`, `docker/`.
- Training script (`src/train.py`) and FastAPI service (`src/api.py`).
- Smoke tests (`tests/test_model.py`, `tests/test_api_smoke.py`).
- Docker support with `docker/Dockerfile`.
- Documentation for Step 1 (`docs/step1.md`) and Step 2 (`docs/step2.md`).

### References
- Milestone: [Milestone 1](https://github.com/anveshyeruva/mlops-qa-bugseverity/milestone/1)
- Release: [Release v0.1](https://github.com/anveshyeruva/mlops-qa-bugseverity/releases/tag/v0.1)

