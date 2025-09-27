import pytest
import json
from pathlib import Path
import joblib, pandas as pd

# These depend on trained artifacts -> run after training in CI
@pytest.mark.integration
def test_artifacts_exist():
    assert Path("models/model.joblib").exists(), "Train first: python src/train.py"
    assert Path("models/metrics.json").exists(), "Train first: python src/train.py"

@pytest.mark.integration
def test_metrics_valid():
    m = json.loads(Path("models/metrics.json").read_text())
    for k in ["accuracy", "f1_macro", "n_train", "n_test", "labels"]:
        assert k in m
    assert 0.0 <= m["accuracy"] <= 1.0

@pytest.mark.integration
def test_predictions_in_label_set():
    df = pd.read_csv("data/bugs.csv")
    labels = set(df["severity"].unique().tolist())
    model = joblib.load("models/model.joblib")
    preds = model.predict([
        "Game crashes after boss fight when saving",
        "Inventory button overlaps on HDR 4k screen",
        "Frame rate drops on city map with many NPCs",
    ])
    for p in preds:
        assert p in labels

