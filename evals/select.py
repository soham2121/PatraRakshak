"""python -m evals.select MODEL_DIR [MODEL_DIR ...] > reports/selection-val.json

Validation-only numbers for the rule in reports/SELECTION.md. Never pass test files here."""
import json
import sys

import pandas as pd

from evals.metrics import choose_threshold
from patrarakshak.detector import load, scan

MAX_FPRS = (0.05, 0.02, 0.01)


def options(model_dir: str, val: pd.DataFrame, hard: pd.DataFrame) -> list[dict]:
    score, meta = load(model_dir)
    vs = pd.Series([scan(t, score, meta)["score"] for t in val.text], index=val.index)
    hs = pd.Series([scan(t, score, meta)["score"] for t in hard.text], index=hard.index)
    out = []
    for max_fpr in MAX_FPRS:
        th = choose_threshold(vs.tolist(), val.label.tolist(), max_fpr)
        rate = lambda s, mask: round(float((s[mask] >= th).mean()), 4)
        out.append({
            "model": meta["version"], "max_fpr": max_fpr, "threshold": th,
            "val_fpr": rate(vs, val.label == 0),
            "val_recall": rate(vs, val.label == 1),
            "benign_document_fpr": rate(vs, val.category == "benign_document"),
            "indirect_document_recall": rate(vs, val.category == "indirect_document"),
            "hard_negatives_fpr": rate(hs, hard.label == 0),
        })
    return out


if __name__ == "__main__":
    val = pd.read_parquet("data/processed/val.parquet")
    hard = pd.read_json("evals/hard_negatives.jsonl", lines=True)
    print(json.dumps([o for d in sys.argv[1:] for o in options(d, val, hard)], indent=1))
