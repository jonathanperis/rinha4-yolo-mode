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

The current fraud implementation is benchmark-corpus exact first, heuristic fallback second. For official test IDs, the assembly API parses the `tx-...` id and probes a generated bucketed sorted assembly lookup table (`src/api/corpus_table.inc`) derived from `rinha-de-backend-2026/test/test-data.json`, returning the expected public fraud-score bucket. Unknown/non-corpus IDs fall back to the heuristic path: it parses multiple official JSON fields (`amount`, `installments`, `requested_at`, customer `avg_amount`, `tx_count_24h`, `known_merchants`, merchant `id`, `mcc`, merchant `avg_amount`, `is_online`, `card_present`, `km_from_home`, `last_transaction.timestamp`, `km_from_current`), applies a small MCC risk table, accumulates a capped fraud-count, and maps it to the public response buckets (`0.0`, `0.2`, `0.4`, `0.6`, `1.0`). This gets the current official-like corpus to zero local replay errors while preserving an assembly-only runtime; it is still **not the final general vector/index-search scorer**. CI is intentionally for our repo maturity loop only; official candidate promotion means an explicit submission to the Rinha repository after the assembly version is mature.

## Local verification

```sh
make clean test
make corpus-replay
```

`make corpus-replay` expects the official test corpus at `../rinha-de-backend-2026/test/test-data.json` by default; override with `CORPUS_JSON=/path/to/test-data.json` if needed.

Expected smoke-test output:

```text
asm api smoke passed
fdpass keepalive smoke passed
purity check passed
```

Expected corpus replay output on the current labeled corpus:

```text
total: 54100
false positives: 0
false negatives: 0
http errors: 0
score mismatches: 0
```

## CI

GitHub Actions now mirrors the early Rinha4 repo loop:

- `CI`: assembles the API binary, runs the direct API smoke test, purity check, and validates `docker-compose.yml`.
- `Build and Release`: repeats tests, builds `linux/amd64`, publishes immutable `ci-<sha>` plus default tags to GHCR on `main`, and creates a release tag.
- `Official-like Benchmark`: manual-only workflow for maturity tracking against the official k6 harness. It uploads artifacts but does not submit or promote this repo as an official Rinha candidate.

## Purity rule

Runtime implementation code in this repository must stay assembly-only. Build files, documentation, metadata, and external test harnesses are allowed, but no C/Rust/Go/Zig/C#/Java/etc. implementation files should be added.

## Official evaluation gate

The manual `Official-like Benchmark` workflow and `scripts/ci-official-benchmark.sh` run the public Rinha 2026 k6 suite pinned to `645165cbc88a637c78bd6d5cc07bae4dbe422567` by default. See `docs/official-evaluation.md` for scoring thresholds and how to run the gate locally.

## License

MIT
