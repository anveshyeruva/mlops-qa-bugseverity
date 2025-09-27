# tests/test_sanity.py
from pathlib import Path

def test_repo_sanity():
    # Tiny check that doesn't require artifacts or API
    assert Path("src/train.py").exists(), "src/train.py missing"
    assert Path("src/api.py").exists(), "src/api.py missing"

