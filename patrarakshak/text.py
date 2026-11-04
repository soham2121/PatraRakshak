import re
import unicodedata

# Zero-width chars, bidi controls, word joiners, BOM, Unicode tag block.
INVISIBLE = re.compile("[​-‏‪-‮⁠-⁤﻿\U000e0000-\U000e007f]")
# Tag characters U+E0020..E007E mirror ASCII and are used to hide instructions; decode, don't drop.
TAGS = {c: c - 0xE0000 for c in range(0xE0020, 0xE007F)}
BOUNDARY = re.compile(r"(?<=[.!?])\s+|\n\s*\n")
# Hard-split pieces of an over-long sentence overlap by this much, so a phrase across a cut is scored whole.
HARD_SPLIT_OVERLAP = 128


def normalize(text: str) -> str:
    """Model input form. Training and serving must both go through this."""
    text = unicodedata.normalize("NFKC", text.translate(TAGS))
    return re.sub(r"\s+", " ", INVISIBLE.sub("", text)).strip()


def signals(text: str) -> list[str]:
    return ["invisible_characters"] if INVISIBLE.search(text) else []


def sentences(text: str) -> list[tuple[int, int]]:
    spans, start = [], 0
    for m in BOUNDARY.finditer(text):
        if text[start:m.start()].strip():
            spans.append((start, m.start()))
        start = m.end()
    if text[start:].strip():
        spans.append((start, len(text)))
    return spans


def chunk(text: str, max_chars: int = 512) -> list[tuple[int, int]]:
    """Windows of whole sentences, <= max_chars, each overlapping the previous by one sentence.
    Never crosses a form feed (the PDF page separator), so every window sits on one page."""
    spans, base = [], 0
    for page in text.split("\f"):
        spans += [(base + s, base + e) for s, e in _windows(page, max_chars)]
        base += len(page) + 1
    return spans


def _windows(text: str, max_chars: int) -> list[tuple[int, int]]:
    sents = [p for s, e in sentences(text) for p in _pieces(s, e, max_chars)]
    out, i = [], 0
    while i < len(sents):
        j = i
        while j + 1 < len(sents) and sents[j + 1][1] - sents[i][0] <= max_chars:
            j += 1
        out.append((sents[i][0], sents[j][1]))
        if j + 1 == len(sents):
            break
        i = max(j, i + 1)
    return out


def _pieces(s: int, e: int, max_chars: int) -> list[tuple[int, int]]:
    """Cuts one sentence into pieces of <= max_chars, each overlapping the previous by HARD_SPLIT_OVERLAP."""
    out = [(s, min(s + max_chars, e))]
    while out[-1][1] < e:
        start = out[-1][1] - HARD_SPLIT_OVERLAP
        out.append((start, min(start + max_chars, e)))
    return out
