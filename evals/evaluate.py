"""python -m evals.evaluate MODEL_DIR FILE [FILE ...]  (FILE = .parquet or .jsonl with text,label[,category])"""
import json
import sys
import time

import pandas as pd

from evals.metrics import summarize
from patrarakshak.detector import load, scan


def main(model_dir: str, *paths: str) -> None:
    score, meta = load(model_dir)
    report = {"model_version": meta["version"], "threshold": meta["threshold"]}
    for path in paths:
        df = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_json(path, lines=True)
        t = time.perf_counter()
        scores = [scan(x, score, meta)["score"] for x in df.text]
        r = summarize(df.label.tolist(), scores, meta["threshold"])
        r["ms_per_text"] = round(1000 * (time.perf_counter() - t) / len(df), 2)
        if "category" in df:
            hit = pd.Series([s >= meta["threshold"] for s in scores], index=df.index)
            r["flag_rate_by_category"] = hit.groupby(df.category).mean().round(3).to_dict()
        report[path] = r
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main(*sys.argv[1:])
