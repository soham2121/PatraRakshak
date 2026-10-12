# Fine-tune runs

Every run, validation numbers only. `test.parquet` was never used for tuning.

| Run | Base | Hyperparameters | Hardware | Val F1 (argmax, per epoch) | Val `benign_document` FPR | Hard-negatives FPR | Notes |
|---|---|---|---|---|---|---|---|
| distilbert-v1 | distilbert-base-uncased | lr 2e-5, batch 16, 3 epochs, max_length 256, seed 42 | RTX 5070 Ti, 92 s | 0.9803 / 0.9809 / 0.9809 | 1.5% at max_fpr 0.05 (thr 0.006); 0.2% at max_fpr 0.01 (thr 0.9963) | 64.7% at max_fpr 0.05; 16.0% at max_fpr 0.01 | Plan hyperparameters unchanged. Best checkpoint by val F1 (epoch 2). |

Only one run was made. The plan's hyperparameters already reached val F1 0.98. The binding constraint is hard negatives, and more tuning against validation would not address it (see `SELECTION.md`).

Not tried: the MuRIL multilingual candidate (`python -m train.finetune models/muril-v1 google/muril-base-cased`). It is worth a run if non-English documents matter, because distilbert-v1 flags benign non-English text (see `distilbert-v1-edge-cases.json`).
