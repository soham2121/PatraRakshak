"""PR_MODEL_DIR=models/X python -m evals.chunk_report FILE [FILE ...]

Prints every scored window of each file (span, token count, score, flagged or not), to see why a document
was or wasn't flagged. TXT files are read as-is; PDF and DOCX go through the same parser as the API."""
import os
import sys
from pathlib import Path

from patrarakshak import detector
from patrarakshak.parse import parse
from patrarakshak.text import chunk, normalize


def main(paths: list[str]) -> None:
    score, meta = detector.load()
    th = meta["threshold"]
    tok = None
    if meta.get("kind") == "transformer":
        from transformers import AutoTokenizer

        tok = AutoTokenizer.from_pretrained(os.getenv("PR_MODEL_DIR"))
    for p in paths:
        text = parse(p, Path(p).read_bytes())[: detector.MAX_CHARS]
        spans = chunk(text)
        texts = [normalize(text[s:e]) for s, e in spans]
        scores = score(texts) if texts else []
        top = max(scores, default=0.0)
        print(f"\n{p}: {len(text)} chars, {len(spans)} windows, max {top:.4f}, threshold {th:.4f}, "
              f"{'suspicious' if top >= th else 'benign'} ({meta['version']})")
        for (s, e), t, sc in zip(spans, texts, scores):
            ntok = f" tok {len(tok(t)['input_ids']):3d}" if tok else ""
            print(f"  {'FLAG' if sc >= th else '    '} [{s:6d},{e:6d}){ntok} {sc:.4f}  {t[:90]}")


if __name__ == "__main__":
    main(sys.argv[1:])
