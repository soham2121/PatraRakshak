"""python -m evals.docs MODEL_DIR DOCS.json"""
import json
import random
import sys

from patrarakshak.detector import load, scan


def make(paragraphs: list[str], attacks: list[str], n: int, seed: int = 0) -> list[dict]:
    """Synthetic documents of 5-15 paragraphs; every second one gets one attack between paragraphs."""
    rng = random.Random(seed)
    docs = []
    for k in range(n):
        paras = rng.sample(paragraphs, rng.randint(5, min(15, len(paragraphs))))
        span = None
        if k % 2:
            attack = rng.choice(attacks)
            pos = rng.randint(0, len(paras))
            start = sum(len(p) + 2 for p in paras[:pos])
            paras.insert(pos, attack)
            span = [start, start + len(attack)]
        docs.append({"text": "\n\n".join(paras), "span": span})
    return docs


def evaluate(docs: list[dict], score_batch, meta: dict) -> dict:
    tp = fn = fp = tn = hits = 0
    for d in docs:
        r = scan(d["text"], score_batch, meta)
        flagged = r["label"] == "suspicious"
        if d["span"] is None:
            fp += flagged
            tn += not flagged
        else:
            s, e = d["span"]
            tp += flagged
            fn += not flagged
            hits += any(g["start"] < e and s < g["end"] for g in r["segments"])
    pos, neg = tp + fn, fp + tn
    return {"doc_recall": tp / pos, "doc_fpr": fp / neg, "span_hit_rate": hits / pos, "n": len(docs)}


if __name__ == "__main__":
    score, meta = load(sys.argv[1])
    print(json.dumps({"model_version": meta["version"], **evaluate(json.load(open(sys.argv[2])), score, meta)}, indent=2))
