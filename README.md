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

The current fraud implementation is a heuristic increment, not the final scorer: it parses multiple official JSON fields (`amount`, `installments`, `tx_count_24h`, `is_online`, `card_present`), accumulates a capped fraud-count, and maps it to all public response buckets (`0.0`, `0.2`, `0.4`, `0.6`, `0.8`, `1.0`). This proves the broader assembly parser/scoring/response path but is still **not submission-ready yet** because the full vectorization/index-search logic is not implemented. CI is intentionally for our repo maturity loop only; official candidate promotion means an explicit submission to the Rinha repository after the assembly version is mature.

## Local verification

```sh
make clean test
```

Expected:

```text
asm api smoke passed
asm lb fdpass smoke passed
asm full fdpass stack smoke passed
purity check passed
```

## CI

GitHub Actions now mirrors the early Rinha4 repo loop:

- `CI`: assembles both binaries, runs direct API, fd-passing LB, full-stack smoke tests, purity check, and validates `docker-compose.yml`.
- `Build and publish image`: repeats tests, builds `linux/amd64`, and publishes immutable `ci-<sha>` plus default tags to GHCR on `main`.
- `Official-like Benchmark`: manual-only workflow for maturity tracking against the official k6 harness. It uploads artifacts but does not submit or promote this repo as an official Rinha candidate.

## Purity rule

Runtime implementation code in this repository must stay assembly-only. Build files, documentation, metadata, and external test harnesses are allowed, but no C/Rust/Go/Zig/C#/Java/etc. implementation files should be added.

## License

MIT
