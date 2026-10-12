"""python -m train.baseline models/tfidf-v1"""
import hashlib
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from evals.metrics import choose_threshold
from patrarakshak.text import normalize

MAX_FPR = 0.05  # validation FPR budget; revisited jointly in Task 12
DATA = Path("data/processed")

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
train, val = (pd.read_parquet(DATA / f"{s}.parquet") for s in ("train", "val"))
pipe = make_pipeline(
    TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
    LogisticRegression(max_iter=2000, class_weight="balanced"),
).fit(train.text.map(normalize), train.label)
val_scores = pipe.predict_proba(val.text.map(normalize))[:, 1]
joblib.dump(pipe, out / "model.joblib")
(out / "meta.json").write_text(json.dumps({
    "kind": "tfidf", "version": out.name, "threshold": choose_threshold(val_scores, val.label, MAX_FPR),
    "max_fpr": MAX_FPR, "hparams": {"ngram_range": [1, 2], "min_df": 2, "C": 1.0},
    "data_sha256": {p: hashlib.sha256((DATA / p).read_bytes()).hexdigest() for p in ("train.parquet", "val.parquet")},
}, indent=1))
