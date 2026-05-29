# rinha4-yolo-mode

Pure x86-64 assembly YOLO-mode participant implementation for [Rinha de Backend 2026](https://github.com/zanfranceschi/rinha-de-backend-2026).

## Goal

This repository is Jonathan Peris' YOLO entry: a pure-assembly backend paired with the shared ASM load balancer from `jonathanperis/rinha4-lb-yolo-mode`.

Final target topology:

```text
k6 / judge
    |
    v
shared asm lb :9999
    |  SCM_RIGHTS fd handoff, round-robin only
    +-- unix:/tmp/rinha/api1.sock -> asm api -> inherited client fd
    +-- unix:/tmp/rinha/api2.sock -> asm api -> inherited client fd
```

## Current status

First fd-passing assembly API stack. The repository now builds only:

- `build/api`: pure-assembly API. With no arguments it runs a direct TCP smoke server on `:9999`; with a Unix-socket path argument it accepts client FDs via `SCM_RIGHTS` and responds on the inherited sockets.

The `docker-compose.yml` default uses a digest-pinned shared ASM LB image from `ghcr.io/jonathanperis/rinha4-lb-yolo-mode` in `fdpass`/`stream` mode instead of bundling a local YOLO LB binary.

The current fraud implementation is a general assembly heuristic path. It parses multiple official JSON fields (`amount`, `installments`, `requested_at`, customer `avg_amount`, `tx_count_24h`, `known_merchants`, merchant `id`, `mcc`, merchant `avg_amount`, `is_online`, `card_present`, `km_from_home`, `last_transaction.timestamp`, `km_from_current`), applies a small MCC risk table, accumulates a capped fraud-count, and maps it to the public response buckets (`0.0`, `0.2`, `0.4`, `0.6`, `1.0`). It intentionally does **not** use preview/test payload IDs or generated corpus lookup tables; every request follows the same payload-derived scoring path.

## Runtime/compose contract

`docker-compose.yml` is the source of truth for the contest-facing topology:

| Service | Contract |
| --- | --- |
| `lb` | Digest-pinned `ghcr.io/jonathanperis/rinha4-lb-yolo-mode` image, `linux/amd64`, public `9999:9999`, bridge networking. |
| LB mode | `LB_MODE=fdpass`, `LB_FDPASS_SOCKET_TYPE=stream`, `LB_FDPASS_SNDBUF=262144`, `UPSTREAMS=/tmp/rinha/api1.sock,/tmp/rinha/api2.sock`. |
| API workers | Two instances of this repo's `/app/api`, launched as `/app/api /tmp/rinha/api1.sock` and `/app/api /tmp/rinha/api2.sock`. |
| Backlog knobs | Compose passes `BACKLOG=65535` to the shared LB; the assembly API direct TCP smoke path keeps its own syscall backlog constant at `BACKLOG=4096`. |
| Resource envelope | LB `0.06 CPU / 30M`; each API `0.47 CPU / 160M`; total declared limit stays inside `1 CPU / 350 MB`. |
| Rule posture | LB only accepts/routes descriptors. Fraud parsing/scoring lives in the API workers, not in the LB. |

## Local verification

```sh
make clean test
```

Expected smoke-test output:

```text
asm api smoke passed
fdpass keepalive smoke passed
docs drift check passed
purity check passed
```

Optional deeper calibration check when the official reference resources are available:

```sh
make oracle-smoke
```

`oracle-smoke` runs `tests/vector_oracle.py` against the assembled API. It is a black-box reference-vector smoke, not a training step: reference payload IDs, labels, and generated lookup artifacts must not be copied into runtime sources. Useful knobs are `RINHA_OFFICIAL_ROOT` for an existing official checkout, `ORACLE_REF_LIMIT` for the number of reference vectors, plus `--resources-root` and `--ref-limit` when invoking the Python script directly.

## CI

GitHub Actions now mirrors the early Rinha4 repo loop:

- `CI`: assembles the API binary, runs the direct API smoke test, fd-pass keepalive smoke, runtime purity check, and validates `docker-compose.yml`.
- `Build and Release`: repeats tests, builds `linux/amd64`, publishes GHCR tags on non-PR runs, and creates a semantic release tag on `main`. Tag families are `latest`, `v<major>.<minor>.<patch>`, immutable `ci-<full-sha>`, and the Docker metadata `sha-*` tag. The workflow ignores docs-only path changes (`docs/**`) unless manually dispatched.
- `Deploy GitHub Pages`: builds the Astro proof dossier under `docs/` and publishes the static site.
- `Official-like Benchmark`: manual-only workflow for maturity tracking against the public Rinha 2026 k6 harness. It uploads artifacts but does not submit or promote this repo as an official Rinha candidate.

## Rule-compliance guardrails

Runtime implementation code in this repository must stay assembly-only and must follow the Rinha rules:

- no preview/test payload IDs, expected labels, or generated lookup tables in runtime sources;
- no fraud-detection logic in the load balancer; it only distributes accepted sockets to API workers;
- compose topology stays on bridge networking, with public linux/amd64 images and total limits at 1 CPU / 350 MB;
- the public evaluator may be used only as a black-box benchmark/calibration gate, never as training data or a runtime reference.

## Official evaluation gate

The manual `Official-like Benchmark` workflow and `scripts/ci-official-benchmark.sh` run the public Rinha 2026 k6 suite at `OFFICIAL_REF=main` by default. Use older refs only for explicitly labeled historical/scoreboard reproduction, never for current promotion evidence. See `docs/official-evaluation.md` for scoring thresholds, rule limits, and how to run the gate locally.

Workflow inputs and local environment variables:

| Workflow input | Script env | Default | Purpose |
| --- | --- | --- | --- |
| `official_ref` | `OFFICIAL_REF` | `main` | Git ref from `zanfranceschi/rinha-de-backend-2026` to clone/fetch. |
| `webapi_image` | `WEBAPI_IMAGE` | empty | Optional prebuilt API image; empty means build from checkout. |
| `benchmark_repetitions` | `BENCHMARK_REPETITIONS` | `1` | Number of k6 repetitions before selecting the representative result. |
| — | `BENCHMARK_K6_MODE` | `native` | k6 execution mode; currently only native k6 is supported. |
| — | `RESULTS_DIR` | `benchmark-results` | Artifact directory for k6 output, selected result, repetition summary, compose logs, and docker state. |

Retained artifacts include `results.json`, `results-repetition-*.json`, `repetition-summary.json`, `k6-output-repetition-*.json`, `k6-report*.html`, `docker-compose.log`, and `docker-state-*.txt`.

## License

MIT
