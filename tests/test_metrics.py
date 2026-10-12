from evals.metrics import choose_threshold, summarize


def test_summarize_counts():
    r = summarize([1, 1, 0, 0], [0.9, 0.2, 0.8, 0.1], threshold=0.5)
    assert r["confusion"] == {"tn": 1, "fp": 1, "fn": 1, "tp": 1}
    assert r["recall"] == 0.5 and r["fpr"] == 0.5 and r["f1"] == 0.5


def test_choose_threshold_caps_fpr():
    neg = [i / 10 for i in range(1, 11)]
    t = choose_threshold(neg + [0.95], [0] * 10 + [1], max_fpr=0.2)
    assert sum(s >= t for s in neg) == 2
