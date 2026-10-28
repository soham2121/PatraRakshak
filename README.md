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

The shipped model is **muril-ens**: the per-window mean of muril-v1 and muril-v3. It needs both releases.

```bash
gh release download model-muril-v1 -R soham2121/PatraRakshak -p muril-v1.tar.gz
gh release download model-muril-ens -R soham2121/PatraRakshak -p muril-ens.tar.gz
tar -xzf muril-v1.tar.gz             # creates models/muril-v1/  (Git Bash on Windows: tar --force-local -xzf ...)
tar -xzf muril-ens.tar.gz            # creates models/muril-v3/ and models/muril-ens/
sha256sum -c models.sha256           # every line must say OK (macOS: shasum -a 256 -c models.sha256)
PR_MODEL_DIR=models/muril-ens uvicorn patrarakshak.api:app
```

`PR_MODEL_DIR=models/muril-v1` still runs muril-v1 alone: half the memory and CPU, with the results in its column below.

Or with Docker: `docker build -t patrarakshak . && docker run -p 8000:8000 -v "$PWD/models:/models:ro" patrarakshak`. The image defaults to `PR_MODEL_DIR=/models/muril-ens`; give the container at least 4 GB of RAM (two models of ~0.9 GB each plus PyTorch).

## Results

Every model is evaluated at its threshold chosen on validation (`reports/SELECTION.md`), and each frozen test set was run once per model. Shipped model: **muril-ens** (since 2026-10-28; muril-v1 from 2026-10-12, distilbert-v1 before that). It won the unchanged selection rule on validation; see the `reports/SELECTION.md` addenda. Model details, error analysis and limitations are in [MODEL_CARD.md](MODEL_CARD.md).

| Metric (set) | Goal | tfidf-v1 | distilbert-v1 | muril-v1 | **muril-ens** | protectai-ref (reference) |
|---|---|---|---|---|---|---|
| In-distribution F1 (`test`) | report only | 0.888 | 0.959 | 0.945 | **0.951** | 0.877 |
| External FPR (wambosec) | ≤ 15% | 2.2% ✅ | 39.4% ❌ | 14.5% ✅ | **4.0% ✅** | 0.5% ✅ |
| External recall (wambosec) | ≥ 0.85 | 0.718 ❌ | 0.896 ✅ | 0.678 ❌ | **0.656 ❌** | 0.822 ❌ |
| Document FPR (`docs_test`, Wikipedia) | ≤ 10% | 0.0% ✅ | 7.5% ✅ | 11.5% ❌ | **11.0% ❌** | 0.0% ✅ |
| Document FPR (`docs_test_domain2`, bills) | ≤ 10% | 0.0% ✅ | 0.5% ✅ | 1.5% ✅ | **3.0% ✅** | 0.5% ✅ |
| Document recall (`docs_test`) | ≥ 0.85 | 0.345 ❌ | 0.965 ✅ | 0.985 ✅ | **0.990 ✅** | 0.645 ❌ |
| Document recall (`docs_test_domain2`) | ≥ 0.85 | 0.370 ❌ | 0.950 ✅ | 0.970 ✅ | **0.955 ✅** | 0.690 ❌ |
| Span hit rate (`docs_test` / domain 2) | ≥ 0.80 | 0.345 / 0.370 ❌ | 0.965 / 0.950 ✅ | 0.980 / 0.965 ✅ | **0.985 / 0.955 ✅** | 0.645 / 0.690 ❌ |
| Hard-negatives FPR | ≤ 20% | 10.7% ✅ | 16.0% ✅ | 18.7% ✅ | **17.3% ✅** | 12.7% ✅ |
| Marathi/Hindi benign FPR (`indic_eval`) | – | – | 100% | 0% | **0%** | – |
| Marathi/Hindi recall (`indic_eval`) | – | – | 1.000 (flags everything) | 0.965 | **0.984** | – |
| Agentic attacks, recall / FPR (`agentic_eval`, validation) | – | – | – | 0.455 / 12.0% | **0.783 / 8.2%** | – |
| BIPIA long documents, recall / FPR (`bipia_eval`, validation) | – | – | – | 0.764 / 32.4% | **0.834 / 38.0%** | – |
| ms per text (CPU, `test`) | – | 0.33 | 19.5 | 35.5 (different PC) | **62** (two models) | 78.5 |

muril-ens cuts external FPR from 14.5% to 4.0% and catches more agentic and hidden-in-document attacks, at twice the memory and CPU of muril-v1. Its misses are external recall (0.656: mostly social-engineering and fiction-framed attacks), Wikipedia document FPR (11.0%), and harmless long documents in the BIPIA set (38% flagged, mostly bank-style transaction emails). The frozen test sets have now been used for five models, so test-side numbers are optimistic. Details are in the model card.

Sources: `reports/<model>-test.json`, `reports/<model>-docs.json`, `reports/<model>-docs-domain2.json`, `reports/<model>-val.json`.

Label policy and data sources: [data/LABELING.md](data/LABELING.md). Current status: [docs/handoff.md](docs/handoff.md). Manual checks still to do: [docs/TESTING.md](docs/TESTING.md).

Implementation plan: [docs/superpowers/plans/2026-10-12-patrarakshak.md](docs/superpowers/plans/2026-10-12-patrarakshak.md)
