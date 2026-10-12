import math

from sklearn.metrics import confusion_matrix


def summarize(labels: list[int], scores: list[float], threshold: float) -> dict:
    preds = [int(s >= threshold) for s in scores]
    tn, fp, fn, tp = confusion_matrix(labels, preds, labels=[0, 1]).ravel().tolist()
    div = lambda a, b: a / b if b else 0.0
    p, r = div(tp, tp + fp), div(tp, tp + fn)
    return {
        "precision": round(p, 4), "recall": round(r, 4), "f1": round(div(2 * p * r, p + r), 4),
        "fpr": round(div(fp, fp + tn), 4), "confusion": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
        "n": len(labels),
    }


def choose_threshold(scores: list[float], labels: list[int], max_fpr: float) -> float:
    """Lowest threshold whose false-positive rate on these (validation!) examples is <= max_fpr."""
    neg = sorted(s for s, y in zip(scores, labels) if y == 0)
    allowed = int(max_fpr * len(neg))
    return math.nextafter(neg[len(neg) - allowed - 1], math.inf)
