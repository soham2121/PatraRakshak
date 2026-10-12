"""Plan edge cases against a real model. Skipped unless PR_TEST_MODEL_DIR points at one (CI has no weights).

PR_TEST_MODEL_DIR=models/distilbert-v1 pytest tests/test_edge_cases.py"""
import os

import pytest

MODEL = os.getenv("PR_TEST_MODEL_DIR")
pytestmark = pytest.mark.skipif(not MODEL, reason="set PR_TEST_MODEL_DIR to a trained model")

# Found by evals/edge_cases.py with distilbert-v1 (reports/distilbert-v1-edge-cases.json).
KNOWN_FAILURES = {
    "devanagari_and_emoji_benign": "non-English and emoji-only text scores ~0.99; training data has no benign non-English text",
    "zero_width_obfuscated_attack": "normalization works; the plain attack also scores 0.9932, just under the strict 0.9963 threshold",
}


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
