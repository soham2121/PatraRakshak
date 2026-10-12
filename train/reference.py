"""python -m train.reference models/protectai-ref

Picks the downloaded reference model's threshold on validation, the same way as for our models.
Download first: huggingface-cli download protectai/deberta-v3-base-prompt-injection-v2 --local-dir models/protectai-ref
"""
import json
import sys
from pathlib import Path

import pandas as pd

from evals.metrics import choose_threshold
from patrarakshak.detector import load
from patrarakshak.text import normalize

MAX_FPR = 0.05
d = Path(sys.argv[1])
meta_path = d / "meta.json"
meta_path.write_text(json.dumps({"kind": "transformer", "version": "protectai-v2-reference", "threshold": 0.5}))
score, meta = load(str(d))
val = pd.read_parquet("data/processed/val.parquet")
meta["threshold"] = choose_threshold(score(val.text.map(normalize).tolist()), val.label.tolist(), MAX_FPR)
meta["max_fpr"] = MAX_FPR
meta_path.write_text(json.dumps(meta, indent=1))
print(json.dumps(meta, indent=1))
