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

Label policy and data sources: [data/LABELING.md](data/LABELING.md). Current status: [docs/handoff.md](docs/handoff.md).

Implementation plan: [docs/superpowers/plans/2026-10-12-patrarakshak.md](docs/superpowers/plans/2026-10-12-patrarakshak.md)
