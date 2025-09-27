# scripts/qa_gate.py
import json, sys
from pathlib import Path

BASELINE_PATH = Path("qa/baseline_metrics.json")
NEW_PATH = Path("models/metrics.json")

# how much drop is allowed before failing the build
TOLERANCE = 0.01  # allow up to 1 percentage point drop

def read_json(p: Path):
    if not p.exists():
        print(f"[qa_gate] Missing file: {p}", file=sys.stderr)
        sys.exit(2)
    return json.loads(p.read_text())

def main():
    baseline = read_json(BASELINE_PATH)
    new = read_json(NEW_PATH)

    b_acc = float(baseline.get("accuracy", -1))
    n_acc = float(new.get("accuracy", -1))
    b_labels = set(baseline.get("labels", []))
    n_labels = set(new.get("labels", []))

    print(f"[qa_gate] Baseline accuracy: {b_acc:.4f}")
    print(f"[qa_gate] New accuracy     : {n_acc:.4f}")
    print(f"[qa_gate] Allowed drop     : {TOLERANCE:.4f}")

    # sanity checks
    if b_acc < 0 or n_acc < 0:
        print("[qa_gate] Invalid metrics.json contents.", file=sys.stderr)
        sys.exit(2)

    # labels should not shrink unexpectedly (basic safety)
    if not b_labels.issubset(n_labels):
        print(f"[qa_gate] ERROR: New labels set {n_labels} does not cover baseline {b_labels}", file=sys.stderr)
        sys.exit(1)

    # regression check
    if n_acc + 1e-12 < b_acc - TOLERANCE:
        print(f"[qa_gate] FAIL: accuracy dropped beyond tolerance ({b_acc:.4f} -> {n_acc:.4f})", file=sys.stderr)
        sys.exit(1)

    print("[qa_gate] PASS: within tolerance (no regression).")
    sys.exit(0)

if __name__ == "__main__":
    main()

