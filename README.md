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
    +-- unix:/run/rinha/api1.sock -> asm api -> inherited client fd
    +-- unix:/run/rinha/api2.sock -> asm api -> inherited client fd
```

## Current status

Bootstrap scaffold. The repository currently builds:

- `build/api`: minimal pure-assembly direct TCP smoke server for `/ready` and fixed `/fraud-score` response.
- `build/lb`: pure-assembly placeholder while the fd-passing LB is ported.

This is **not submission-ready yet**. See `docs/plans/2026-05-16-yolo-assembly-participation.md` for the implementation plan.

## Local verification

```sh
make clean test
```

Expected:

```text
asm api smoke passed
purity check passed
```

## Purity rule

Runtime implementation code in this repository must stay assembly-only. Build files, documentation, metadata, and external test harnesses are allowed, but no C/Rust/Go/Zig/C#/Java/etc. implementation files should be added.

## License

MIT
