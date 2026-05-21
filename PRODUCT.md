# PRODUCT.md: rinha4-yolo-mode Pages

_Last updated: 2026-05-18_

## Product identity

`rinha4-yolo-mode` is Jonathan Peris' pure x86-64 assembly Rinha de Backend 2026 participant. The public Pages surface should read as the assembly sibling of the C and .NET proof dossiers, not as a separate portfolio microsite. It proves a specific runtime bet: assembly API workers, shared YOLO load balancer, fd-passing transport, and every claim tied to code, compose limits, CI, or replay artifacts.

## Register

brand

## Primary users

1. **Rinha reviewers and competitors** checking whether the participant is legitimate, reproducible, and within contest constraints.
2. **Systems engineers** curious about assembly-only HTTP handling, Linux syscalls, Unix sockets, and fd-passing under tight CPU and memory limits.
3. **Future Jonathan and agents** who need a source-backed map of the architecture before tuning, benchmarking, or preparing a submission branch.

## Reference sites

This Pages surface is intentionally a variant of:

- `https://jonathanperis.github.io/rinha4-back-end-c/`
- `https://jonathanperis.github.io/rinha4-back-end-dotnet/`

It should reuse the family grammar: CRT dark surface, monospace, proof ledger, lane labels, benchmark console, runtime trace, report CTAs, and evidence caveats. It must replace C and .NET specifics with assembly/YOLO specifics.

## Visitor state of mind

Visitors arrive skeptical. They need proof quickly: what is assembly, what is shared infrastructure, which commands verify it, what changed recently, and where the docs explain the runtime without hype.

## Core value propositions

- Pure assembly API runtime, built with GNU `as` and `ld`.
- Shared ASM load balancer default from `jonathanperis/rinha4-lb-yolo-mode`.
- fd-passing topology: LB accepts TCP on `9999`, distributes accepted client FDs over Unix sockets to two API processes.
- Current local corpus replay baseline reports `54100` total cases with `0` false positives, `0` false negatives, `0` HTTP errors, and `0` score mismatches when the official public corpus is available.
- GitHub Actions publishes immutable GHCR tags and runs CI, build/release, Pages, and manual official-like benchmark loops.

## Canonical facts for site copy

- Repo name: `rinha4-yolo-mode`.
- Challenge: Rinha de Backend 2026.
- Runtime implementation rule: repository-owned runtime implementation code must stay assembly-only.
- Default runtime composition: one shared ASM LB plus two API instances.
- API command in compose: `/app/api /tmp/rinha/api1.sock` and `/app/api /tmp/rinha/api2.sock`.
- LB default image: digest-pinned `ghcr.io/jonathanperis/rinha4-lb-yolo-mode` image from `docker-compose.yml`.
- Default LB mode: `fdpass`, socket type `stream`, send buffer `262144`.
- Resource split in compose: LB `0.04 CPU / 30M`, each API `0.48 CPU / 160M`.
- Verification commands: `make clean test`, `make corpus-replay`, `docker compose config --quiet`.

## Brand voice

- **Physical words:** phosphor, audited, register-level, pressure-tested.
- **Tone:** concise, technical, explicit about maturity and caveats.
- **Avoid:** generic "blazing fast" claims, neon cyber filler, hero-number theatrics without provenance, vague enterprise language.
- **Prefer:** lane labels, command snippets, topology traces, exact service names, links to evidence.

## Desired visitor experience

The page should feel like the third member of the Rinha4 proof-dossier family. It opens like a hostile benchmark terminal, then proves itself through lane-labeled evidence and a runtime trace. The assembly identity should be obvious without pretending CI numbers are official hardware.

## A/B testing hypotheses

- `?ab=evidence`: leads with lane-labeled proof and corpus replay.
- `?ab=ledger`: emphasizes provenance cards and source links.
- `?ab=runtime`: emphasizes fd-passing, `_start`, and the syscall path.

Primary success signals are GitHub Pages availability, docs route visits, GitHub source clicks, and reduced repeated questions about topology, verification, and what is assembly-only.
