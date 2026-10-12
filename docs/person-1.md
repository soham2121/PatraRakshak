# PatraRakshak: Person 1 work (models)

You own the models. Everything else (data build, metrics, parsing, API, UI, Docker) is being built by Persons 2 and 3. Your job is to train two candidate models plus a reference model, and then lead the model side of selection and release.

The full plan, with exact code, is `docs/superpowers/plans/2026-10-12-patrarakshak.md`. This page tells you which parts are yours, what order to do them in, and what you're waiting on.

## Summary

| # | Task | What you produce | Where you run it | Size |
|---|---|---|---|---|
| 8 | TF-IDF + LogisticRegression baseline | `train/baseline.py`, `models/tfidf-v1/`, `reports/tfidf-v1-dev.json` | Laptop, about 30 s | Small |
| 10 | DistilBERT fine-tune + protectai reference | `train/finetune.py`, `models/distilbert-v1/`, `models/protectai-ref/`, `reports/finetune-runs.md`, CPU latency note | Kaggle/Colab T4, about 20 min per run | Medium |
| 12 | Model selection (all three people) | `reports/SELECTION.md`, `reports/*-val.json`, `*-test.json`, `*-docs.json`, README results table | Laptop | Medium |
| 13 | Release: your part | Model uploaded to HF or a GitHub Release, SHA-256 in `MODEL_CARD.md`, fetch command in README | Anywhere | Small |

Already done and on `main`: Task 1 (repo, CI) and Task 2 (`patrarakshak/text.py`, `patrarakshak/detector.py`). `detector.load()` already knows how to load both a `tfidf` and a `transformer` model directory, so your models plug into the app without any code changes.

## What you're waiting on

| You need | Comes from | Status |
|---|---|---|
| `evals/metrics.py` (`choose_threshold`), `evals/evaluate.py`, `evals/hard_negatives.jsonl` | Task 4 (Person 2) | ✅ on main |
| `data/build.py` → `data/processed/{train,val,test}.parquet`, `external_wambosec.parquet` | Task 3 (Person 2) | ✅ on main |
| `evals/docs.py`, `docs_test.json`, `docs_test_domain2.json` | Task 9 (Person 2) | ✅ on main |
| `patrarakshak/api.py`, `tests/fixtures/sample.pdf` | Tasks 5–6 (Person 3) | ✅ on main |

**Nothing blocks you any more.** Build the data with `python -m data.build`; it takes a few minutes because it streams Wikipedia. Then check that your file hashes match the table in `data/LABELING.md`. If a frozen file's hash differs, get the file from the team drive instead. You no longer need the quick export below.

## Setup

```bash
git clone https://github.com/soham2121/PatraRakshak.git && cd PatraRakshak
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash; use .venv/bin/activate on Linux/Mac
pip install -e ".[train,dev]"
pytest -q   # should pass
```

Work on your own branch (for example `p1-models`). Run every command from the repo root: `python -m train.baseline` needs that to import `evals` and `patrarakshak`.

**(Obsolete now that Task 3 is on main.)** This writes the neuralchemy `core` split to the paths the scripts read. It's good enough to debug the scripts, but every number you get from it must be re-run once `python -m data.build` exists.

```python
# scratch only, do not commit
from pathlib import Path
from datasets import load_dataset
Path("data/processed").mkdir(parents=True, exist_ok=True)
for split, ds in load_dataset("neuralchemy/Prompt-injection-dataset", "core").items():
    name = {"validation": "val"}.get(split, split)
    ds.to_pandas()[["text", "label"]].to_parquet(f"data/processed/{name}.parquet")
```

## Task 8: Baseline (plan section "Task 8")

1. Create `train/baseline.py` with the code from the plan, unchanged.
2. Run `python -m train.baseline models/tfidf-v1`. This writes `model.joblib` and `meta.json`, which holds the threshold chosen on validation at 5% FPR.
3. Run `mkdir -p reports && python -m evals.evaluate models/tfidf-v1 data/processed/val.parquet evals/hard_negatives.jsonl > reports/tfidf-v1-dev.json`.
4. Look at the per-category output:
   - `benign_document` FPR shows whether the Wikipedia benign data helped.
   - The hard-negatives FPR is the known weak spot.
5. Smoke-test it in the app: `PR_MODEL_DIR=models/tfidf-v1 uvicorn patrarakshak.api:app` (needs Task 6). This needs no test changes.
6. Commit the script and the report JSON, **not** the model: `git commit -m "feat: TF-IDF baseline"`.

## Task 10: DistilBERT + reference model (plan section "Task 10")

1. Create `train/finetune.py` with the code from the plan. On Kaggle or Colab (T4):
   - clone the repo
   - run `pip install -e ".[train]"`
   - copy `data/processed/` up
   - run `python -m train.finetune models/distilbert-v1`
   - download `models/distilbert-v1/` without `checkpoints/`, and delete `checkpoints/` afterwards
2. **Tune only against validation.** Log every run in `reports/finetune-runs.md`, one row per run: hyperparameters, validation F1, validation `benign_document` FPR, hard-negatives FPR. Never look at `test.parquet`.
3. Set up the reference model:
   - Run `huggingface-cli download protectai/deberta-v3-base-prompt-injection-v2 --local-dir models/protectai-ref`.
   - Check that `config.json` has `id2label["1"]` as the injection class. The detector assumes index 1 is positive. If it isn't, note that and skip the model.
   - Score `val.parquet` with it and pick its threshold with `choose_threshold(scores, labels, 0.05)`, exactly as for our models.
   - Write `models/protectai-ref/meta.json`: `{"kind": "transformer", "version": "protectai-v2-reference", "threshold": <chosen>}`.
   - Check the license on the model card. It's for evaluation only.
4. Check the CPU path on a laptop:
   - Run `PR_MODEL_DIR=models/distilbert-v1 uvicorn patrarakshak.api:app`.
   - Scan `tests/fixtures/sample.pdf` (needs Tasks 5–6).
   - Record the latency in `reports/`.
5. `git commit -m "feat: DistilBERT fine-tune script and reference model setup"`.

## Task 12: Selection (all three people, you drive the model side)

Order matters here. It's what keeps the test set honest.

1. **Before looking at any numbers**, write the selection rule in `reports/SELECTION.md`. The recommended rule:
   - Pick the highest validation `indirect_document` recall.
   - It must have validation `benign_document` FPR ≤ 5% and hard-negatives FPR ≤ 20%.
   - Break ties in favor of the smaller or faster model.
2. For each of `tfidf-v1`, `distilbert-v1` and `protectai-ref`, run `python -m evals.evaluate models/X data/processed/val.parquet evals/hard_negatives.jsonl > reports/X-val.json`. Apply the rule. If you change `max_fpr`, recompute the threshold from **validation** scores only and save it in `meta.json`.
3. Run the frozen test sets **once** per model, then never re-run them:
   - `python -m evals.evaluate models/X data/processed/test.parquet data/processed/external_wambosec.parquet > reports/X-test.json`
   - `python -m evals.docs models/X data/processed/docs_test.json > reports/X-docs.json`
   - the same docs command for `docs_test_domain2.json`, writing `reports/X-docs-domain2.json`
4. Fill in the README results table against the targets in the plan. Mark misses ❌ and don't hide them.
5. Run the plan's edge cases through the app with the real model. Turn any new failure into a test.

## Task 13: Release (your part)

1. Upload `models/<chosen>/` to a Hugging Face model repo or a GitHub Release.
2. Record its SHA-256 in `MODEL_CARD.md`.
3. Add the fetch and verify commands to the README.
4. Load it in a fresh virtualenv on a second machine.

## Rules that apply to you

- Never commit model weights, `data/processed/`, or downloaded datasets. `models/` and `data/processed/` are already gitignored.
- `test.parquet` is frozen. No thresholds, hyperparameters or model choices may come from it.
- Every number you report comes from a script writing JSON into `reports/`.
- Thresholds live in each model's `meta.json` and are always chosen on validation.
- If you have to change the plan's code, write down what you changed and why in your PR description.
