# Official evaluation test-suite gate

This repo uses the public Rinha de Backend 2026 test suite as an official-like rejection gate.

Pinned public evaluation reference:

- upstream: `zanfranceschi/rinha-de-backend-2026`
- ref: `64acf788baef3c1687bba93c04357cc8c7082b11`
- docs: `docs/en/EVALUATION.md`
- k6 script/data: `test/test.js`, `test/test-data.json`

The official docs state the public k6 script may differ from the final evaluator, so local/GitHub runs here are calibration evidence, not automatic official promotion. The public evaluator is used only as a black-box test harness: its payloads and expected labels must not be copied into runtime sources, generated into lookup artifacts, or used as fraud-reference data.

## Rinha rules this gate must preserve

- The official FAQ and submission docs forbid using test payloads as a reference or fraud lookup.
- The load balancer must not inspect payloads, apply conditionals, respond early, or run detection logic.
- The submitted topology must expose port `9999`, use bridge networking, avoid privileged/host modes, and fit inside 1 CPU / 350 MB total declared limits.
- Submission images must be public and linux/amd64-compatible; source repositories must remain public and MIT-licensed.

## Score facts that matter

- `final_score = p99_score + detection_score`.
- `p99 <= 1ms` saturates `p99_score` at `3000`; sub-1ms work does not add official score.
- `p99 > 2000ms` cuts latency to `-3000`.
- Weighted detection errors are `E = 1*FP + 3*FN + 5*HTTP errors`.
- If `(FP + FN + HTTP errors) / total > 15%`, detection score is fixed at `-3000`.
- HTTP errors are the worst failure mode; prefer a valid fast fallback response over throwing/timeout paths.

## Run locally

```sh
OFFICIAL_REF=64acf788baef3c1687bba93c04357cc8c7082b11 \
BENCHMARK_REPETITIONS=3 \
BENCHMARK_K6_MODE=native \
bash scripts/ci-official-benchmark.sh
```

For GitHub Actions, run the benchmark workflow and keep `official_ref=64acf788baef3c1687bba93c04357cc8c7082b11` unless intentionally checking a newer upstream test suite.

## Promotion interpretation

- Correctness/stability gate: `false_positive_detections=0`, `false_negative_detections=0`, `http_errors=0` is the desired candidate lane.
- .NET score-max target: official-like p99 must cross below `1ms`; below `~1.024ms` is the current useful threshold to beat the high .NET score lane.
- C/YOLO lanes already below `1ms` in prior official evidence; for them this gate mainly guards regressions and verifies participant-file restoration/retests.
