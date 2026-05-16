# rinha4-yolo-mode

Pure x86-64 assembly YOLO-mode participant implementation for [Rinha de Backend 2026](https://github.com/zanfranceschi/rinha-de-backend-2026).

## Goal

This repository is Jonathan Peris' YOLO entry: the backend implementation **and** its custom load balancer are being written in assembly, carrying over the proven topology from the C and custom-LB repositories.

Final target topology:

```text
k6 / judge
    |
    v
asm lb :9999
    |  SCM_RIGHTS fd handoff, round-robin only
    +-- unix:/tmp/rinha/api1.sock -> asm api -> inherited client fd
    +-- unix:/tmp/rinha/api2.sock -> asm api -> inherited client fd
```

## Current status

First fd-passing assembly stack. The repository currently builds:

- `build/api`: pure-assembly API. With no arguments it runs a direct TCP smoke server on `:9999`; with a Unix-socket path argument it accepts client FDs via `SCM_RIGHTS` and responds on the inherited sockets.
- `build/lb`: pure-assembly TCP listener on `:9999` that round-robins accepted client FDs to `/tmp/rinha/api1.sock` and `/tmp/rinha/api2.sock`.

The current fraud implementation is a rule-based heuristic scorer. The assembly API parses multiple official JSON fields (`amount`, `installments`, `requested_at`, customer `avg_amount`, `tx_count_24h`, `known_merchants`, merchant `id`, `mcc`, merchant `avg_amount`, `is_online`, `card_present`, `km_from_home`, `last_transaction.timestamp`, `km_from_current`), applies a small MCC risk table, accumulates a capped fraud-count, and maps it to the public response buckets (`0.0`, `0.2`, `0.4`, `0.6`, `1.0`). It intentionally does not use the public test payloads as an ID lookup so the repository can be submitted under the official rules. It is still **not the final general vector/index-search scorer**. CI is intentionally for our repo maturity loop only; official candidate promotion means an explicit submission to the Rinha repository after the assembly version is mature.

## Local verification

```sh
make clean test
make corpus-replay
```

`make corpus-replay` expects the official test corpus at `../rinha-de-backend-2026/test/test-data.json` by default; override with `CORPUS_JSON=/path/to/test-data.json` if needed.

Expected smoke-test output:

```text
asm api smoke passed
asm lb fdpass smoke passed
asm full fdpass stack smoke passed
purity check passed
```

Corpus replay is useful as a diagnostic against the public sample data, but it is not a release gate and the heuristic scorer is not expected to match every public labeled payload exactly.

## CI

GitHub Actions now mirrors the early Rinha4 repo loop:

- `CI`: assembles both binaries, runs direct API, fd-passing LB, full-stack smoke tests, purity check, and validates `docker-compose.yml`.
- `Build and publish image`: repeats tests, builds `linux/amd64`, and publishes immutable `ci-<sha>` plus default tags to GHCR on `main`.
- `Official-like Benchmark`: manual-only workflow for maturity tracking against the official k6 harness. It uploads artifacts but does not submit or promote this repo as an official Rinha candidate.

## Purity rule

Runtime implementation code in this repository must stay assembly-only. Build files, documentation, metadata, and external test harnesses are allowed, but no C/Rust/Go/Zig/C#/Java/etc. implementation files should be added.

## License

MIT
