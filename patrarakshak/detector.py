import json
import os
from pathlib import Path

from .text import chunk, normalize, signals

MAX_CHARS = 100_000


def _mock(texts: list[str]) -> list[float]:
    return [0.9 if "ignore previous instructions" in t.lower() else 0.1 for t in texts]


def load(model_dir: str | None = None):
    """Returns (score_batch, meta). No model dir configured -> mock backend."""
    model_dir = model_dir or os.getenv("PR_MODEL_DIR")
    if not model_dir:
        return _mock, {"kind": "mock", "version": "mock-0", "threshold": 0.5}
    d = Path(model_dir)
    meta = json.loads((d / "meta.json").read_text())
    if meta["kind"] == "tfidf":
        import joblib

        pipe = joblib.load(d / "model.joblib")
        return (lambda texts: pipe.predict_proba(texts)[:, 1].tolist()), meta
    if meta["kind"] == "ensemble":
        # Mean of member scores per window; members are model dirs relative to this one.
        members = [load(str(d / m))[0] for m in meta["members"]]
        return (lambda texts: [sum(s) / len(s) for s in zip(*(f(texts) for f in members))]), meta

    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(d)
    model = AutoModelForSequenceClassification.from_pretrained(d).eval()

    def score(texts: list[str], batch_size: int = 32) -> list[float]:
        out = []
        with torch.inference_mode():
            for i in range(0, len(texts), batch_size):
                enc = tok(texts[i:i + batch_size], truncation=True, max_length=256, padding=True, return_tensors="pt")
                out += model(**enc).logits.softmax(-1)[:, 1].tolist()  # index 1 = positive class
        return out

    return score, meta


def scan(text: str, score_batch, meta: dict) -> dict:
    truncated = len(text) > MAX_CHARS
    text = text[:MAX_CHARS]
    spans = chunk(text)
    scores = score_batch([normalize(text[s:e]) for s, e in spans]) if spans else []
    th = meta["threshold"]
    top = max(scores, default=0.0)
    return {
        "label": "suspicious" if top >= th else "benign",
        "score": top,
        "threshold": th,
        "model_version": meta["version"],
        "chunks_scanned": len(spans),
        "truncated": truncated,
        "signals": signals(text),
        "segments": [
            {"start": s, "end": e, "text": text[s:e], "score": sc}
            for (s, e), sc in zip(spans, scores)
            if sc >= th
        ],
    }
