"""python -m train.finetune models/distilbert-v1 [BASE_MODEL]

BASE_MODEL defaults to distilbert-base-uncased; pass google/muril-base-cased for the multilingual candidate.
PR_SMOKE=N trains on N rows for one epoch (CPU check only; never report those numbers).
PR_EXTRA_TRAIN=indic_train appends data/processed/indic_train.parquet to train (see data/build_indic.py)."""
import hashlib
import json
import os
import sys
from pathlib import Path

import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import f1_score
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, Trainer,
                          TrainingArguments, set_seed)

from evals.metrics import choose_threshold
from patrarakshak.text import normalize

BASE = sys.argv[2] if len(sys.argv) > 2 else "distilbert-base-uncased"
SEED, MAX_FPR = 42, 0.05
SMOKE = int(os.getenv("PR_SMOKE", "0"))
EXTRA = [e.strip() for e in os.getenv("PR_EXTRA_TRAIN", "").split(",") if e.strip()]  # Windows `set X=a && ...` keeps the space
HP = {"lr": 2e-5, "batch": 16, "epochs": 1 if SMOKE else 3, "max_length": 256}
DATA = Path("data/processed")
out = Path(sys.argv[1])

set_seed(SEED)
tok = AutoTokenizer.from_pretrained(BASE)


def load_split(name: str, extra: list[str] = []) -> Dataset:
    df = pd.concat([pd.read_parquet(DATA / f"{n}.parquet") for n in [name, *extra]], ignore_index=True)
    if SMOKE:
        df = df.sample(SMOKE, random_state=SEED)
    ds = Dataset.from_dict({"text": df.text.map(normalize).tolist(), "label": df.label.tolist()})
    return ds.map(lambda b: tok(b["text"], truncation=True, max_length=HP["max_length"]), batched=True)


train, val = load_split("train", EXTRA), load_split("val")
model = AutoModelForSequenceClassification.from_pretrained(
    BASE, num_labels=2, id2label={0: "benign", 1: "suspicious"}, label2id={"benign": 0, "suspicious": 1})
args = TrainingArguments(
    str(out / "checkpoints"), learning_rate=HP["lr"], per_device_train_batch_size=HP["batch"],
    per_device_eval_batch_size=64, num_train_epochs=HP["epochs"], eval_strategy="epoch",
    save_strategy="epoch", load_best_model_at_end=True, metric_for_best_model="f1",
    save_total_limit=1, seed=SEED, report_to=[])
trainer = Trainer(model=model, args=args, train_dataset=train, eval_dataset=val, processing_class=tok,
                  compute_metrics=lambda p: {"f1": f1_score(p.label_ids, p.predictions.argmax(-1))})
trainer.train()
trainer.save_model(str(out))
val_scores = torch.tensor(trainer.predict(val).predictions).softmax(-1)[:, 1].tolist()
(out / "meta.json").write_text(json.dumps({
    "kind": "transformer", "version": out.name, "base": BASE, "seed": SEED, "hparams": HP,
    "threshold": choose_threshold(val_scores, val["label"], MAX_FPR), "max_fpr": MAX_FPR,
    "data_sha256": {p: hashlib.sha256((DATA / p).read_bytes()).hexdigest()
                    for p in ("train.parquet", "val.parquet", *(f"{e}.parquet" for e in EXTRA))},
}, indent=1))
