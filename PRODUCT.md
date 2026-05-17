# PRODUCT.md: rinha4-yolo-mode Pages

_Last updated: 2026-05-17_

## Product identity

`rinha4-yolo-mode` is Jonathan Peris' pure x86-64 assembly Rinha de Backend 2026 participant. The repository proves a specific runtime bet: keep the API implementation assembly-only, use a shared assembly load balancer for fd-passing, and make every performance claim traceable to code, compose limits, CI, or benchmark artifacts.

## Register

brand

## Primary users

1. **Rinha reviewers and competitors** checking whether the participant is legitimate, reproducible, and within contest constraints.
2. **Systems engineers** curious about assembly-only HTTP handling, Linux syscalls, Unix sockets, and fd-passing under tight CPU and memory limits.
3. **Future Jonathan and agents** who need a source-backed map of the architecture before tuning, benchmarking, or preparing a submission branch.

## Visitor state of mind

Visitors arrive skeptical. They need proof quickly: what is assembly, what is shared infrastructure, which commands verify it, what changed recently, and where the docs explain the runtime without hype.

## Core value propositions

- Pure assembly API runtime, built with GNU `as` and `ld`.
- Shared ASM load balancer default from `jonathanperis/rinha4-lb-yolo-mode`.
- fd-passing topology: LB accepts TCP on `9999`, distributes accepted client FDs over Unix sockets to two API processes.
- Current local corpus replay baseline reports `54100` total cases with `0` false positives, `0` false negatives, `0` HTTP errors, and `0` score mismatches when the official public corpus is available.
- GitHub Actions publishes immutable GHCR tags and runs CI, build, CodeQL, and official-like benchmark loops.

## Canonical facts for site copy

- Repo name: `rinha4-yolo-mode`.
- Challenge: Rinha de Backend 2026.
- Runtime implementation rule: repository-owned runtime implementation code must stay assembly-only.
- Default runtime composition: one shared ASM LB plus two API instances.
- API command in compose: `/app/api /tmp/rinha/api1.sock` and `/app/api /tmp/rinha/api2.sock`.
- LB default image tag: `ghcr.io/jonathanperis/rinha4-lb-yolo-mode:asm-ci-dcc6b89ca9d21c7a8dbb1588a6bfbbc0bd20bb91`.
- Default LB mode: `fdpass`, socket type `stream`, send buffer `262144`.
- Resource split in compose: LB `0.08 CPU / 30M`, each API `0.46 CPU / 160M`.
- Verification commands: `make clean test`, `make corpus-replay`, `docker compose config --quiet`.

## Brand voice

- **Physical words:** bare-metal, audited, pressure-tested.
- **Tone:** concise, technical, explicit about maturity and caveats.
- **Avoid:** generic "blazing fast" claims, neon cyber filler, hero-number theatrics, vague enterprise language.
- **Prefer:** source-backed statements, command snippets, topology diagrams, exact service names, links to evidence.

## Desired visitor experience

The page should feel like opening an operator dossier, not a SaaS landing page. It should preserve the dark technical aesthetic but replace generic terminal cosplay with an inspectable architecture workbench: topology first, evidence second, docs paths third.

## Current site gap

GitHub Pages was configured but returned a Pages 404 because no workflow deployed a static artifact. This site exists to close that gap and turn the repo from source-only to publicly navigable documentation.

## A/B testing hypotheses

- `control`: concise proof-led landing page with docs-first CTA.
- `proof`: moves verification and result evidence into the hero for skeptical reviewers.
- `architecture`: moves topology and fd-passing mechanics into the first viewport for systems readers.

Primary success signals are GitHub Pages availability, docs route visits, GitHub source clicks, and reduced repeated questions about topology, verification, and what is assembly-only.
