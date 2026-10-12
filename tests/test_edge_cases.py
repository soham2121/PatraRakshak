"""Plan edge cases against a real model. Skipped unless PR_TEST_MODEL_DIR points at one (CI has no weights).

PR_TEST_MODEL_DIR=models/muril-v1 pytest tests/test_edge_cases.py"""
import json
import os
from pathlib import Path

import pytest

MODEL = os.getenv("PR_TEST_MODEL_DIR")
pytestmark = pytest.mark.skipif(not MODEL, reason="set PR_TEST_MODEL_DIR to a trained model")

# Known failures per model version, found by evals/edge_cases.py (reports/<model>-edge-cases.json).
KNOWN_FAILURES_BY_MODEL = {
    "distilbert-v1": {
        "devanagari_and_emoji_benign": "non-English and emoji-only text scores ~0.99; training data has no benign non-English text",
        "zero_width_obfuscated_attack": "normalization works; the plain attack also scores 0.9932, just under the strict 0.9963 threshold",
    },
    "muril-v1": {
        "docx_attack_only_in_comment": "the comment-only attack scores 0.967, under the 0.9819 threshold",
    },
}
KNOWN_FAILURES = KNOWN_FAILURES_BY_MODEL.get(json.loads((Path(MODEL) / "meta.json").read_text())["version"], {}) if MODEL else {}


@pytest.fixture(scope="module")
def client():
    os.environ["PR_MODEL_DIR"] = MODEL
    import importlib

    from fastapi.testclient import TestClient

    import patrarakshak.api as api

    yield TestClient(importlib.reload(api).app)
    os.environ.pop("PR_MODEL_DIR")


def _cases():
    from evals.edge_cases import CASES

    for name, case in CASES.items():
        marks = [pytest.mark.xfail(reason=KNOWN_FAILURES[name], strict=True)] if name in KNOWN_FAILURES else []
        yield pytest.param(*case, id=name, marks=marks)


@pytest.mark.parametrize("kwargs,status,label", list(_cases()) if MODEL else [])
def test_edge_case(client, kwargs, status, label):
    r = client.post("/api/v1/scan", **kwargs)
    assert r.status_code == status
    if label:
        assert r.json()["label"] == label
