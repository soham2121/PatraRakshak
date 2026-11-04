"""Agentic training data and two extra eval sets. Run after data.build: python -m data.build_extra

Writes to data/processed/ (never touches the frozen files):
- agentic_train.parquet: 3nesdeniz/agentic-prompt-injection-5k `train` split (CC-BY-4.0).
- agentic_eval.parquet: its `validation` split. Its `test` split is never used.
- bipia_eval.parquet: 1,000 whole documents from MAlmasabi/Indirect-Prompt-Injection-BIPIA-GPT
  (CC-BY-SA-4.0, gated), eval only. Not trained on: every benign row is GPT-written and every attack row is
  from BIPIA (a style shortcut), and the attack's position inside the document isn't given.
"""
import hashlib
import json

import pandas as pd
from datasets import load_dataset

from data.build import COLS, OUT, SEED, near_dups


def agentic(split: str) -> pd.DataFrame:
    d = load_dataset("3nesdeniz/agentic-prompt-injection-5k", split=split).to_pandas()
    return d.assign(category=d.attack_family + "/" + d.technique, source="agentic5k")[COLS]


def bipia(n: int = 500) -> pd.DataFrame:
    d = load_dataset("MAlmasabi/Indirect-Prompt-Injection-BIPIA-GPT", split="train").to_pandas()
    d = d.drop_duplicates("context")
    d = pd.concat([g.sample(n, random_state=SEED) for _, g in d.groupby("label")])
    category = d.label.map({0: "benign_document_gpt", 1: "bipia_attack_document"})
    return pd.DataFrame({"text": d.context, "label": d.label, "category": category, "source": "bipia_gpt"})[COLS]


def main() -> None:
    frozen = pd.concat([pd.read_parquet(OUT / f).text for f in ("val.parquet", "test.parquet", "external_wambosec.parquet")])
    train = agentic("train").reset_index(drop=True)
    train = train[~near_dups(train.text, frozen.reset_index(drop=True)).values]
    train.to_parquet(OUT / "agentic_train.parquet")
    agentic("validation").to_parquet(OUT / "agentic_eval.parquet")
    bipia().to_parquet(OUT / "bipia_eval.parquet")
    files = ("agentic_train.parquet", "agentic_eval.parquet", "bipia_eval.parquet")
    for f in files:
        df = pd.read_parquet(OUT / f)
        print(f, len(df), "label 1 / 0:", int(df.label.sum()), "/", int((df.label == 0).sum()))
    print(json.dumps({f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in files}, indent=1))


if __name__ == "__main__":
    main()
