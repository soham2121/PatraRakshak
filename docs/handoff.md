# Handoff: state as of 2026-10-12

Plan: `docs/superpowers/plans/2026-10-12-patrarakshak.md`. Person 1's brief: `docs/person-1.md`.

## Done (on main)

| Task | Owner | What landed | Verified by |
|---|---|---|---|
| 1 | P3 | Repo skeleton, CI | CI config, `pytest` |
| 2 | P1 (done early) | `patrarakshak/text.py`, `detector.py` (mock / tfidf / transformer backends) | `tests/test_text.py`, `tests/test_detector.py` |
| 4 | P2 | `evals/metrics.py`, `evals/evaluate.py`, `evals/hard_negatives.jsonl` (150 benign + 40 quoted-attack lines) | `tests/test_metrics.py`; `python -m evals.evaluate "" evals/hard_negatives.jsonl` runs |
| 9 | P2 | `evals/docs.py` (synthetic documents with planted attacks, doc-level eval) | `tests/test_docs_eval.py` |
| 3 | P2 | `data/build.py`, `data/LABELING.md` (label policy, taxonomy, provenance, hashes) | `python -m data.build` ran: 117 near-dups dropped, test = 942 rows, hashes recorded |
| 5 | P3 | `patrarakshak/parse.py`, PDF fixtures | `tests/test_parse.py` |
| 6 | P3 | `POST /api/v1/scan` in `patrarakshak/api.py` | `tests/test_api.py`; curl against a running server |
| 7 | P3 | React UI in `web/`; CI now builds it | `npm run build`; built UI served by FastAPI |

Whole suite: **31 passed**, and `npm run build` passes.

## Not finished

1. **Task 11 (Docker): written, not verified.** `Dockerfile` and `.dockerignore` are committed, but `docker build` was never run. Next steps:
   - Run `docker build -t patrarakshak .`.
   - Run `docker run -p 8000:8000 -e PR_MODEL_DIR= patrarakshak`. The empty `PR_MODEL_DIR` uses the mock until `models/tfidf-v1` exists.
   - Scan `tests/fixtures/sample.pdf`. Expected: Suspicious, page 2.
   - Once Person 1 has a model, run it with `-v "$PWD/models/tfidf-v1:/models:ro"` instead.
2. **Frozen data upload (Task 3, Step 4).** Copy `data/processed/test.parquet`, `docs_test.json` and `docs_test_domain2.json` to the team's shared drive. Their hashes are in `data/LABELING.md`. Anyone who rebuilds should compare hashes and use the drive copy if theirs differ.
3. **UI keyboard check (Task 7).** No browser was available here, so tab through the page once by hand:
   - Every control should be reachable and labelled.
   - Run `uvicorn patrarakshak.api:app` and `cd web && npm run dev`.
4. **Whole-branch review.** Nobody has reviewed Tasks 3–7, 9 and 11 yet. Do this before Task 12.
5. **Person 1's work.** Tasks 8 and 10 are unblocked; see `docs/person-1.md`.
6. **Joint tasks.** Tasks 12 (selection) and 13 (release) need Person 1's models first.

## Decisions taken that deviate from the plan

Each line shows the decision, followed by the cost if it's wrong.

- **Python version.** The local venv uses Python 3.13, while CI pins 3.11. *If wrong:* a 3.11-only failure would show up only in CI.
- **Task order.** Tasks ran in the order 4 → 9 → 3 → 5 → 6 → 7 → 11, because `data/build.py` imports `evals.docs`. *If wrong:* nothing.
- **Second document domain (Task 9).** Steps 4–5 were done inside Task 3. The second domain is **FiscalNote/billsum `ca_test`** (CC0, first 600 California bills), written to `docs_test_domain2.json`. *If wrong:* swap the corpus and re-hash.
- **PDF fixtures (Task 5).** They were generated with fpdf2 and Pillow, not exported from Word. Both are only installed in the venv, not project dependencies. *If wrong:* regenerate them by hand.
- **wambosec categories (Task 3).** wambosec benign rows have no category, so `build.py` fills in `benign`. *If wrong:* it's a one-line change.
- **Taxonomy (Task 3).** It is a roll-up table in `LABELING.md`; the processed files keep each dataset's raw categories. wambosec has about 300 free-form labels. *If wrong:* add a mapping in `evaluate.py` later.
- **Train size (Task 3).** `train.parquet` has 9,356 rows; the plan estimated 7k–9k. *If wrong:* nothing.
- **`.dockerignore` (Task 11).** Added `.venv/` and `.superpowers/` so the build context stays small. *If wrong:* nothing.

## Small things noticed, not fixed

- `web/README.md` is still the Vite template README.
- CI uses Node 20; Vite 8 needs Node ≥ 20.19, which `setup-node@v4` with `20` currently resolves to.

## How to run

```bash
pip install -e ".[dev]"            # add ,train for data build / training
python -m data.build               # a few minutes, writes data/processed/
pytest -q
uvicorn patrarakshak.api:app       # mock model unless PR_MODEL_DIR is set
cd web && npm ci && npm run build  # FastAPI then serves the UI at /
```
