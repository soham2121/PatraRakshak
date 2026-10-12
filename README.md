# PatraRakshak

Scans pasted text and TXT/PDF/DOCX files for prompt-injection passages. It is a detector, not a guarantee.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
```

Implementation plan: [docs/superpowers/plans/2026-10-12-patrarakshak.md](docs/superpowers/plans/2026-10-12-patrarakshak.md)
