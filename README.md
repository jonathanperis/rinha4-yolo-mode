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

## Local verification

```sh
make clean test
```


Expected smoke-test output:

```text
asm api smoke passed
fdpass keepalive smoke passed
purity check passed
```


## CI

GitHub Actions now mirrors the early Rinha4 repo loop:

- `CI`: assembles the API binary, runs the direct API smoke test, purity check, and validates `docker-compose.yml`.
- `Build and Release`: repeats tests, builds `linux/amd64`, publishes immutable `ci-<sha>` plus default tags to GHCR on `main`, and creates a release tag.
- `Official-like Benchmark`: manual-only workflow for maturity tracking against the official k6 harness. It uploads artifacts but does not submit or promote this repo as an official Rinha candidate.

## Rule-compliance guardrails

Runtime implementation code in this repository must stay assembly-only and must follow the Rinha rules:

- no preview/test payload IDs, expected labels, or generated lookup tables in runtime sources;
- no fraud-detection logic in the load balancer; it only distributes accepted sockets to API workers;
- compose topology stays on bridge networking, with public linux/amd64 images and total limits at 1 CPU / 350 MB;
- the public evaluator may be used only as a black-box benchmark/calibration gate, never as training data or a runtime reference.

## Official evaluation gate

The manual `Official-like Benchmark` workflow and `scripts/ci-official-benchmark.sh` run the public Rinha 2026 k6 suite pinned to `64acf788baef3c1687bba93c04357cc8c7082b11` by default. See `docs/official-evaluation.md` for scoring thresholds, rule limits, and how to run the gate locally.

## License

MIT
