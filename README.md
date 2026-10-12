# PatraRakshak

Scans pasted text and TXT/PDF/DOCX files for prompt-injection passages. It is a detector, not a guarantee.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
```

## Run

```bash
pip install -e ".[dev,train]"
python -m data.build                 # builds data/processed/ (a few minutes)
cd web && npm ci && npm run build && cd ..
uvicorn patrarakshak.api:app         # http://localhost:8000; set PR_MODEL_DIR=models/<name> for a real model
```

## Get the trained model

```bash
gh release download model-distilbert-v1 -R soham2121/PatraRakshak -p distilbert-v1.tar.gz
tar -xzf distilbert-v1.tar.gz        # creates models/distilbert-v1/
sha256sum -c models.sha256           # every line must say OK
PR_MODEL_DIR=models/distilbert-v1 uvicorn patrarakshak.api:app
```

Or with Docker: `docker build -t patrarakshak . && docker run -p 8000:8000 -v "$PWD/models/distilbert-v1:/models:ro" patrarakshak`.

## Results

Every model is evaluated at its threshold chosen on validation (`reports/SELECTION.md`), and each frozen test set was run once. Shipped model: **distilbert-v1**. Model details, error analysis and limitations are in [MODEL_CARD.md](MODEL_CARD.md).

| Metric (set) | Goal | tfidf-v1 | **distilbert-v1** | protectai-ref (reference) |
|---|---|---|---|---|
| In-distribution F1 (`test`) | report only | 0.888 | **0.959** | 0.877 |
| External FPR (wambosec) | ≤ 15% | 2.2% ✅ | **39.4% ❌** | 0.5% ✅ |
| External recall (wambosec) | ≥ 0.85 | 0.718 ❌ | **0.896 ✅** | 0.822 ❌ |
| Document FPR (`docs_test`, Wikipedia) | ≤ 10% | 0.0% ✅ | **7.5% ✅** | 0.0% ✅ |
| Document FPR (`docs_test_domain2`, bills) | ≤ 10% | 0.0% ✅ | **0.5% ✅** | 0.5% ✅ |
| Document recall (`docs_test`) | ≥ 0.85 | 0.345 ❌ | **0.965 ✅** | 0.645 ❌ |
| Document recall (`docs_test_domain2`) | ≥ 0.85 | 0.370 ❌ | **0.950 ✅** | 0.690 ❌ |
| Span hit rate (`docs_test` / domain 2) | ≥ 0.80 | 0.345 / 0.370 ❌ | **0.965 / 0.950 ✅** | 0.645 / 0.690 ❌ |
| Hard-negatives FPR | ≤ 20% | 10.7% ✅ | **16.0% ✅** | 12.7% ✅ |
| ms per text (CPU, `test`) | – | 0.33 | 19.5 | 78.5 |

The main miss is distilbert-v1's external FPR (39.4%). Most of those false positives are benign questions containing non-Latin scripts, escaped code points or encoding vocabulary. The model also flags benign non-English text in general. Both are covered in the model card.

Sources: `reports/<model>-test.json`, `reports/<model>-docs.json`, `reports/<model>-docs-domain2.json`, `reports/<model>-val.json`.

Label policy and data sources: [data/LABELING.md](data/LABELING.md). Current status: [docs/handoff.md](docs/handoff.md). Manual checks still to do: [docs/TESTING.md](docs/TESTING.md).

Implementation plan: [docs/superpowers/plans/2026-10-12-patrarakshak.md](docs/superpowers/plans/2026-10-12-patrarakshak.md)
