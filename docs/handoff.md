# Handoff: state as of 2026-10-12 (updated after Tasks 8, 10–12)

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

| 8 | P1 | `train/baseline.py`; `models/tfidf-v1` trained locally; `reports/tfidf-v1-dev.json` | data hashes match `LABELING.md` |
| 10 | P1 | `train/finetune.py`, `train/reference.py`; `distilbert-v1` trained (92 s, RTX 5070 Ti); `protectai-ref` thresholded on val | `reports/finetune-runs.md`, `reports/latency.md` |
| 11 | P3 | Docker image builds (2.0 GB) and serves the UI; with `distilbert-v1` mounted, `sample.pdf` → Suspicious, page 2 | `docker build`, `docker run` |
| 12 | all | `reports/SELECTION.md` (rule written first), `evals/select.py`, val/test/docs reports, README results table, `evals/edge_cases.py` + `tests/test_edge_cases.py` | frozen test sets run once per model |

Whole suite: **31 passed, 1 skipped** (the skip is the real-model edge-case test). With `PR_TEST_MODEL_DIR=models/distilbert-v1`: 36 passed, 2 xfailed (known failures, see `MODEL_CARD.md`). `npm run build` passes.

## Not finished

Step-by-step checklist for everything below: [docs/TESTING.md](TESTING.md).

1. **Model upload (Task 13): done.** Releases `model-distilbert-v1` and `model-muril-v1`, both checked on a second machine (see the 2026-10-12 update below).
2. **Frozen data upload (Task 3, Step 4).** Copy `data/processed/test.parquet`, `docs_test.json` and `docs_test_domain2.json` to the team drive. A rebuild on 2026-10-12 reproduced all six hashes exactly.
3. **UI keyboard check (Task 7).** Not done by hand, and the UI was restyled on 2026-10-28, so use the updated checklist in `TESTING.md` §1. All controls are native, labelled elements.
4. **Whole-branch review** of Tasks 3–12, by a person, plus the 2026-10-28 changes below.
5. **Known model weaknesses of muril-ens** (`MODEL_CARD.md`): external recall 0.656 (target ≥ 0.85), mostly social-engineering and fiction-framed attacks; attacks quoted inside explanatory prose are often missed; 38% of harmless BIPIA long documents and 11.0% of Wikipedia documents are flagged; non-English text other than Marathi/Hindi is unreliable; HTML entities are not decoded (`html.unescape` in `normalize` needs a retrain).
7. **Second-machine check of muril-ens** (`TESTING.md` §2) and **Azure deployment** (container with at least 4 GB of RAM, `models/` mounted, `PR_MODEL_DIR=/models/muril-ens`).
6. **Marathi/Hindi UI strings** (`web/src/i18n.ts`) need review by a native speaker.

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

- CI uses Node 20; Vite 8 needs Node ≥ 20.19, which `setup-node@v4` with `20` currently resolves to.

## How to run

```bash
pip install -e ".[dev]"            # add ,train for data build / training
python -m data.build               # a few minutes, writes data/processed/
pytest -q
uvicorn patrarakshak.api:app       # mock model unless PR_MODEL_DIR is set
cd web && npm ci && npm run build  # FastAPI then serves the UI at /
```

## Decisions taken in Tasks 8–12

- **Training hardware.** Everything trained on a local RTX 5070 Ti (CUDA 12.8 torch), not Kaggle or Colab. *If wrong:* nothing; the scripts are unchanged.
- **Thresholds come from scan-level scores.** `evals/select.py` scores validation through `detector.scan`, the same path the evaluator and the app use, not raw text. *If wrong:* thresholds move slightly.
- **Selection rule with an explicit `max_fpr` grid** {0.05, 0.02, 0.01}. All three models ship at their 0.01 option. *If wrong:* change the rule in `SELECTION.md` and re-run validation only.
- **`training_args.bin` dropped from `models/distilbert-v1/`.** It is a pickle and isn't needed to load the model. *If wrong:* nothing.
- **UI shows scores to 4 decimals.** At 3 decimals, a score of 0.9962 against a threshold of 0.99632 displayed as equal but was not flagged.

## Update from Person 1 (branch `p1-indic`, 2026-10-12)

- **Task 13, second machine: done.** macOS check passed: checksums OK, 36 passed / 2 xfailed, `sample.pdf` flagged on page 2. Frozen-data rebuild hashes also matched on macOS (`docs/TESTING.md` ticked).
- **Marathi/Hindi:** `distilbert-v1` flags 100% of Marathi/Hindi text, including plain application forms. `data/build_indic.py` adds `indic_train` / `indic_eval` (hashes in `data/LABELING.md`), and `train/finetune.py` takes `PR_EXTRA_TRAIN=indic_train`.
- **`muril-v1` candidate:** trained on an RTX 3060 (642 s). It passes the selection rule on validation, has 0% FPR on Marathi/Hindi benign text, and meets the external FPR target (14.5%). It loses external recall (0.678) and is at 11.5% Wikipedia document FPR. Full comparison: `reports/SELECTION.md` addendum. Weights: GitHub Release `model-muril-v1`.
- **Decision taken: `muril-v1` is now the shipped model** (GitHub Release `model-muril-v1`; `models.sha256`, README, MODEL_CARD and TESTING updated). `tests/test_edge_cases.py` keeps known failures per model version, so both models still test cleanly. `distilbert-v1` remains in Release `model-distilbert-v1`.

## Update 2026-10-28

- **UI restyled** as a lab-style screening report (teal letterhead, result table with value / reference / H flag, flagged-passage table), with an EN / मराठी / हिंदी switch. New: `web/src/app.css`, `web/src/i18n.ts`, font package `@fontsource/mukta`. Design records: `PRODUCT.md`, `DESIGN.md`, `.impeccable/`. Checked in headless Chrome at 1440 and 390 px with real muril-v1 scans; keyboard check still open.
- **Long-document misses investigated.** Hand-written reconstructions of the manual tests are in `tests/fixtures/longdocs/`. The pipeline was checked end to end (character windows of ≤ 512 chars at 44–104 tokens, so no truncation; batch and single scores agree to 1e-6; decision is `max >= threshold`; API equals detector). Cause: model scores, not code. A social-engineering attack's window scored 0.864 while benign advice in the same guide scored 0.934, so no threshold separates them; an attack quoted inside explanatory prose scores ~0.03–0.23 while the bare quote scores 0.993.
- **Tests:** deterministic chunking and decision tests in `tests/test_text.py` and `tests/test_detector.py`; real-model long-document cases in `tests/test_longdocs.py` (skipped without `PR_TEST_MODEL_DIR`, known muril-v1 misses as strict xfails). Whole suite: 39 passed, 3 skipped. With `PR_TEST_MODEL_DIR=models/muril-v1`: `test_longdocs.py` + `test_edge_cases.py` give 12 passed, 7 xfailed.
- **Chunking fix:** a sentence over 512 chars is now hard-split into pieces overlapping by 128 chars (`HARD_SPLIT_OVERLAP` in `patrarakshak/text.py`), so a phrase across a cut is scored whole. muril-v1's validation selection numbers did not change.
- **Diagnostic tool:** `PR_MODEL_DIR=models/muril-v1 python -m evals.chunk_report FILE ...` prints every window's span, token count and score.
- **muril-v2 tried and rejected.** `data/build_hard.py` (social-engineering and quoted-in-prose attacks, dolly-15k procedural benign text; hashes in `data/LABELING.md`). Big recall gains on `hard_eval`, but hard-negatives FPR 39.3% (limit 20%), so it fails the selection rule. Details: `reports/SELECTION.md` addendum. Frozen test sets were not run for it. Weights were deleted, never released. **muril-v1 remains the shipped model.**

## Update 2026-10-28 (later): shipped model is now muril-ens

- **New data:** `data/build_extra.py` builds `agentic_train` / `agentic_eval` (3nesdeniz/agentic-prompt-injection-5k) and `bipia_eval` (1,000 whole BIPIA documents, eval only). Hashes in `data/LABELING.md`. The BIPIA dataset is gated: log in with `.venv/Scripts/hf.exe auth login` and accept its terms before rebuilding.
- **muril-v3** (train + indic_train + agentic_train) passed the rule's limits but lost step 3 to muril-v1. **muril-ens**, the per-window mean of muril-v1 and muril-v3 (`"kind": "ensemble"` in `detector.load`), won step 3 and is the shipped model. External FPR 4.0% (was 14.5%), external recall 0.656 (was 0.678). Full numbers: `reports/SELECTION.md` addendum, README, `MODEL_CARD.md`.
- **Release:** `model-muril-ens` holds `muril-ens.tar.gz` (models/muril-v3/ and models/muril-ens/); muril-v1 stays in `model-muril-v1`. `models.sha256` lists all eleven files.
- **Docker:** the image now defaults to `PR_MODEL_DIR=/models/muril-ens`; mount the whole `models/` directory. Give it at least 4 GB of RAM.
- **Tests:** muril-ens passes every edge case (including the DOCX comment that muril-v1 missed) and has the same six known long-document misses as muril-v1, recorded as strict xfails in `tests/test_longdocs.py`.
