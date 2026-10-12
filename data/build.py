"""Build processed datasets. Run once: python -m data.build. Prints file hashes for meta.json."""
import hashlib
import json
import random
from pathlib import Path

import pandas as pd
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from evals.docs import make as make_docs
from patrarakshak.text import chunk

OUT = Path("data/processed")
SEED = 42
COLS = ["text", "label", "category", "source"]
rng = random.Random(SEED)


def near_dups(train: pd.Series, others: pd.Series, cutoff: float = 0.9) -> pd.Series:
    """True for train rows with TF-IDF cosine >= cutoff to any val/test row (86 test rows hit this)."""
    v = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit(pd.concat([train, others]))
    sim = cosine_similarity(v.transform(train), v.transform(others)).max(1)
    return pd.Series(sim >= cutoff, index=train.index)


def doc_chunks(texts) -> list[str]:
    """First <=400-char window of each paragraph of at least 200 chars."""
    out = []
    for t in texts:
        for p in t.split("\n"):
            if len(p) >= 200:
                s, e = chunk(p, 400)[0]
                out.append(p[s:e])
    return out


def wiki_chunks(start: int, n: int) -> list[str]:
    """Paragraph chunks from Wikipedia articles [start, start+n)."""
    ds = load_dataset("wikimedia/wikipedia", "20231101.en", split="train", streaming=True).skip(start).take(n)
    return doc_chunks(a["text"] for a in ds)


def with_docs(df: pd.DataFrame, paras: list[str], name: str) -> pd.DataFrame:
    """Add k benign document chunks and k attacks embedded in other document chunks."""
    rng.shuffle(paras)
    k = min(len(paras) // 2, int((df.label == 1).sum()))
    attacks = df[df.label == 1].text.sample(k, random_state=SEED).tolist()
    embedded = [f"{p} {a}" if rng.random() < 0.5 else f"{a} {p}" for a, p in zip(attacks, paras[k:2 * k])]
    extra = pd.DataFrame({
        "text": paras[:k] + embedded,
        "label": [0] * k + [1] * k,
        "category": ["benign_document"] * k + ["indirect_document"] * k,
        "source": f"wikipedia_{name}",
    })
    return pd.concat([df[COLS], extra], ignore_index=True)


def main() -> None:
    nc = load_dataset("neuralchemy/Prompt-injection-dataset", "core")
    tr, va, te = (nc[s].to_pandas() for s in ("train", "validation", "test"))
    drop = near_dups(tr.text, pd.concat([va.text, te.text]))
    print(f"dropping {drop.sum()} train rows near-duplicating val/test")
    tr = tr[~drop]

    OUT.mkdir(parents=True, exist_ok=True)
    with_docs(tr, wiki_chunks(0, 3000), "train").to_parquet(OUT / "train.parquet")
    with_docs(va, wiki_chunks(3000, 600), "val").to_parquet(OUT / "val.parquet")
    te[COLS].to_parquet(OUT / "test.parquet")  # published test split, frozen

    wb = load_dataset("wambosec/prompt-injections")
    ext = pd.concat([wb[s].to_pandas() for s in wb]).rename(columns={"prompt": "text"}).assign(source="wambosec")
    ext["category"] = ext.category.fillna("benign")  # benign rows have no category
    ext[COLS].to_parquet(OUT / "external_wambosec.parquet")

    docs = make_docs(wiki_chunks(3600, 600), te[te.label == 1].text.tolist(), n=400, seed=SEED)
    (OUT / "docs_test.json").write_text(json.dumps(docs))
    # Second domain: California bill text (FiscalNote/billsum, CC0), so document FPR isn't Wikipedia-only.
    bills = load_dataset("FiscalNote/billsum", split="ca_test")["text"][:600]
    docs2 = make_docs(doc_chunks(bills), te[te.label == 1].text.tolist(), n=400, seed=SEED)
    (OUT / "docs_test_domain2.json").write_text(json.dumps(docs2))

    print(json.dumps({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir())}, indent=1))


if __name__ == "__main__":
    main()
