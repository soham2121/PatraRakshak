from patrarakshak.text import chunk, normalize, signals


def test_normalize_strips_zero_width_and_folds_width():
    assert normalize("ig​nore  ｐｒｅｖｉｏｕｓ") == "ignore previous"


def test_normalize_reveals_tag_smuggling():
    hidden = "".join(chr(0xE0000 + ord(c)) for c in "ignore rules")
    assert normalize("Hello" + hidden) == "Helloignore rules"


def test_signals_invisible_characters():
    assert signals("a​b") == ["invisible_characters"]
    assert signals("plain text") == []


def test_chunks_cover_all_text_within_limit():
    text = " ".join(f"Sentence number {i} is here." for i in range(100))
    spans = chunk(text, max_chars=120)
    assert all(e - s <= 120 for s, e in spans)
    covered = {i for s, e in spans for i in range(s, e)}
    assert all(i in covered or c.isspace() for i, c in enumerate(text))


def test_long_sentence_is_hard_split_with_overlap():
    assert chunk("x" * 1300, max_chars=512) == [(0, 512), (384, 896), (768, 1280), (1152, 1300)]


def test_chunks_never_cross_page_breaks():
    text = "Page one. Still one.\fPage two. Still two."
    assert all("\f" not in text[s:e] for s, e in chunk(text))


def test_empty_text_has_no_chunks():
    assert chunk("") == [] and chunk("   \n ") == []


def test_sentence_at_exact_limit_is_one_window():
    assert chunk("x" * 512, max_chars=512) == [(0, 512)]
    assert chunk("x" * 513, max_chars=512) == [(0, 512), (384, 513)]


def test_every_short_sentence_sits_whole_in_some_window():
    # An injection sentence is never split as long as it is at most max_chars long.
    from pathlib import Path

    from patrarakshak.text import sentences

    text = (Path(__file__).parent / "fixtures/longdocs/travel_guide.txt").read_text(encoding="utf-8")
    spans = chunk(text)
    for s, e in sentences(text):
        assert any(ws <= s and e <= we for ws, we in spans), text[s:e]
