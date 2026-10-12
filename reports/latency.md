# CPU latency

## End to end, in the Docker image (CPU-only torch)

`POST /api/v1/scan` with `tests/fixtures/sample.pdf` (301 chars, 2 chunks). The model was mounted read-only, there was one warm-up request first, then five timed requests. Host: Ryzen 7 9800X3D running Docker Desktop.

| Model | Seconds per request (5 runs) |
|---|---|
| distilbert-v1 | 0.259, 0.293, 0.466, 0.212, 0.249 |
| tfidf-v1 | 0.0055, 0.0053, 0.0052, 0.0050, 0.0052 |

The first request to distilbert-v1 after start-up took 1.1 s, which includes model warm-up.

## Per text, from the evaluator

These figures are `ms_per_text` in `*-test.json`. The evaluator runs in-process on the host CPU, but other jobs were running at the same time, so treat them as upper bounds.

## Large inputs (distilbert-v1, host CPU, from `distilbert-v1-edge-cases.json`)

- 150k characters, truncated to 100k (291 chunks): about 3.2 s.
- The same paragraph repeated 1,000 times (250 chunks): about 2.7 s.
