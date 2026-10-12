# Model selection

## Rule (written 2026-10-12, before any candidate's validation per-category numbers were looked at)

Candidates: `tfidf-v1`, `distilbert-v1`, `protectai-ref` (reference only; it is not shipped unless the team decides otherwise).

Every number below comes from validation (`data/processed/val.parquet`) or `evals/hard_negatives.jsonl`. The test files are not used for selection.

1. For each candidate, compute thresholds on validation scores with `choose_threshold` at `max_fpr` in {0.05, 0.02, 0.01}. That gives up to nine (model, threshold) options.
2. Keep the options with validation `benign_document` flag rate ≤ 5% and hard-negatives FPR ≤ 20%.
3. Among those, pick the highest validation `indirect_document` recall. Ties go to the smaller or faster model.
4. If no option passes step 2, keep the options that pass the `benign_document` limit, pick the one with the lowest hard-negatives FPR, and report the hard-negatives miss as a miss.
5. `protectai-ref` is only a comparison point. If it wins, the shipped model is the best of our own two under the same rule, and the gap is reported.

The chosen threshold is written into that model's `meta.json`. The frozen test sets (`test.parquet`, `external_wambosec.parquet`, `docs_test*.json`) are then run once per model.

## Outcome (from `reports/selection-val.json`)

| Option | Threshold | Val `benign_document` FPR | Hard-negatives FPR | Val `indirect_document` recall | Passes? |
|---|---|---|---|---|---|
| tfidf-v1 @ 0.05 | 0.521 | 3.2% | 70.7% | 66.1% | no (hard negatives) |
| tfidf-v1 @ 0.02 | 0.659 | 0.2% | 26.7% | 46.3% | no (hard negatives) |
| tfidf-v1 @ 0.01 | 0.753 | 0.0% | 10.7% | 33.9% | yes |
| distilbert-v1 @ 0.05 | 0.006 | 1.5% | 64.7% | 99.6% | no (hard negatives) |
| distilbert-v1 @ 0.02 | 0.942 | 0.2% | 43.3% | 99.1% | no (hard negatives) |
| **distilbert-v1 @ 0.01** | **0.9963** | **0.2%** | **16.0%** | **97.9%** | **yes, selected** |
| protectai-ref @ 0.05 | 0.001 | 4.9% | 36.0% | 81.5% | no (hard negatives) |
| protectai-ref @ 0.02 | 0.036 | 0.6% | 28.7% | 71.7% | no (hard negatives) |
| protectai-ref @ 0.01 | 0.997 | 0.0% | 12.7% | 60.5% | yes |

**Shipped model: `distilbert-v1` at threshold 0.996322274208069.** The comparison models were also set to their passing option (`max_fpr` 0.01) before the test sets were run.

Hard negatives were the binding constraint for every model. At `max_fpr` 0.05, every candidate flags more than a third of benign text that only discusses or quotes instructions.
