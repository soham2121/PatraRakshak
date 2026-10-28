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

## Addendum: multilingual candidate `muril-v1` (2026-10-12, branch `p1-indic`)

`muril-v1` is `google/muril-base-cased` fine-tuned on `train.parquet` + `indic_train.parquet` (`data/build_indic.py`), with the same hyperparameters as `distilbert-v1`. It was added after the rule above was written and was judged by that unchanged rule, on validation only (`reports/muril-v1-selection-val.json`):

| Option | Threshold | Val `benign_document` FPR | Hard-negatives FPR | Val `indirect_document` recall | Passes? |
|---|---|---|---|---|---|
| muril-v1 @ 0.05 | 0.006 | 1.1% | 89.3% | 99.8% | no (hard negatives) |
| muril-v1 @ 0.02 | 0.960 | 0.4% | 36.7% | 98.9% | no (hard negatives) |
| **muril-v1 @ 0.01** | **0.9819** | **0.2%** | **18.7%** | **98.1%** | **yes** |

By the rule's step 3, muril-v1 @ 0.01 (98.1% `indirect_document` recall) edges out distilbert-v1 @ 0.01 (97.9%). **The shipped model is not changed by this addendum.** The trade-offs below are a team decision.

Test-side numbers, run once for muril-v1. The frozen sets had already been used for the first three models, so treat them as slightly optimistic (`docs/TESTING.md`).

| Metric (set) | Goal | distilbert-v1 | muril-v1 |
|---|---|---|---|
| In-distribution F1 (`test`) | report only | 0.959 | 0.945 |
| External FPR (wambosec) | ≤ 15% | 39.4% ❌ | **14.5% ✅** |
| External recall (wambosec) | ≥ 0.85 | 0.896 ✅ | 0.678 ❌ |
| Document FPR (`docs_test` / domain 2) | ≤ 10% | 7.5% / 0.5% ✅ | 11.5% ❌ / 1.5% ✅ |
| Document recall (`docs_test` / domain 2) | ≥ 0.85 | 0.965 / 0.950 ✅ | 0.985 / 0.970 ✅ |
| Span hit rate (`docs_test` / domain 2) | ≥ 0.80 | 0.965 / 0.950 ✅ | 0.980 / 0.965 ✅ |
| Hard-negatives FPR (val-side) | ≤ 20% | 16.0% ✅ | 18.7% ✅ |
| `indic_eval` FPR (Marathi/Hindi benign) | – | **100%** | **0%** |
| `indic_eval` recall (Marathi/Hindi attacks) | – | 100% (flags everything) | 96.5% |
| ms per text (`test`, CPU) | – | 19.5 | 35.5 (a different PC's CPU, so not directly comparable) |

`indic_eval` breakdown for muril-v1: `benign_document` 0%, `benign_form` 0% (this includes the Marathi/Hindi "ignore my previous application" lines), `english_attack_in_document` 99.2%, `native_attack_in_document` 97.5%, standalone `native_attack` with unseen template phrasing 68.8% (n = 16).

Edge cases (`reports/muril-v1-edge-cases.json`): the benign Devanagari+emoji case and the zero-width attack now pass, but the attack hidden only in a DOCX comment scores 0.967, under the 0.982 threshold, and is missed.

**Reading.** muril-v1 fixes the non-English false-positive problem and meets the external FPR target, but it loses external recall (mostly English social-engineering and obfuscation rows) and goes over the Wikipedia document FPR target. If Marathi/Hindi documents are in scope, which the Seva pitch says they are, muril-v1 is the only candidate that is usable on them. The Marathi/Hindi eval is small and template-based, so its numbers show the direction, not production accuracy.

**Decision (2026-10-12): ship `muril-v1`.** The team switched the shipped model to `muril-v1` because the product targets Marathi/Hindi government forms, and `distilbert-v1` can't be used on them (100% FPR on `indic_eval`). The switch is also consistent with the rule's step 3 on validation (98.1% vs 97.9% `indirect_document` recall). The accepted costs are lower external recall (0.678) and a Wikipedia document FPR of 11.5%; both are listed as misses in the README. `distilbert-v1` stays available as GitHub Release `model-distilbert-v1`.

## Addendum: candidate `muril-v2` (2026-10-28), rejected

Motivation: manual long-document tests (`tests/fixtures/longdocs/`, `tests/test_longdocs.py`) showed muril-v1 missing social-engineering attacks and attacks quoted inside explanatory prose. The pipeline was checked first and is not the cause: the attack windows really score under the threshold.

`muril-v2` is `google/muril-base-cased` fine-tuned on `train` + `indic_train` + `hard_train` (`data/build_hard.py`), same hyperparameters as muril-v1, trained in 290 s on an RTX 5070 Ti. Judged by the unchanged rule above, on validation only, after the chunking change of the same day (over-long sentences are now split with a 128-char overlap; muril-v1's numbers did not move). Source: `reports/muril-v2-selection-val.json`.

| Option | Threshold | Val `benign_document` FPR | Hard-negatives FPR | Val `indirect_document` recall | Passes? |
|---|---|---|---|---|---|
| muril-v2 @ 0.05 | 0.002 | 0.9% | 83.3% | 99.8% | no (hard negatives) |
| muril-v2 @ 0.02 | 0.963 | 0.2% | 45.3% | 99.1% | no (hard negatives) |
| muril-v2 @ 0.01 | 0.9896 | 0.2% | 39.3% | 98.5% | no (hard negatives) |

**No option passes step 2, so muril-v1 stays the shipped model.** The frozen test sets were not run for muril-v2.

What it gained and what it cost, at each model's 0.01 option (`reports/muril-v2-val.json`; validation-side sets only):

| Set / category | muril-v1 | muril-v2 |
|---|---|---|
| `hard_eval` social engineering in a document (recall) | 75.8% | 97.5% |
| `hard_eval` quoted in prose (recall) | 94.0% | 99.0% |
| `hard_eval` benign procedural (FPR) | 1.1% | 0.2% |
| `indic_eval` FPR / recall | 0% / 96.5% | 0% / 99.2% |
| Hard negatives: quoted example without an operative instruction (FPR) | 10.0% | 53.3% |
| Hard negatives: security discussion (FPR) | 6.7% | 40.0% |
| Hard negatives: technical docs (FPR) | 40.0% | 60.0% |

Reading: training on quoted-in-prose attacks taught the model that quoting or discussing instructions is itself suspicious. `hard_eval` gains are also partly template recall: on the hand-written long-document fixtures muril-v2 still misses all three social-engineering passages, while it does catch the quoted attack in the cybersecurity article and no longer flags the admissions guide. A next candidate needs benign training text that discusses and quotes attacks without containing one. The muril-v2 weights were deleted and never released; rebuild with `python -m data.build_hard` and `PR_EXTRA_TRAIN=indic_train,hard_train python -m train.finetune models/muril-v2 google/muril-base-cased`.
