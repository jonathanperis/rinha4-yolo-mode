# YOLO Assembly Participation Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build Jonathan Peris' YOLO-mode Rinha de Backend 2026 participation in `rinha4-yolo-mode` with implementation and custom load balancer written in pure x86-64 assembly.

**Architecture:** The final runtime mirrors the proven C entry: a custom load balancer accepts TCP on port `9999`, distributes connections round-robin to two API instances, and hands accepted client file descriptors over Unix sockets using `SCM_RIGHTS`. API instances parse HTTP/JSON directly from inherited client sockets, vectorize requests, query a preprocessed IVF index, and return one of six prebuilt fraud-score responses.

**Tech Stack:** GNU assembler `.S` with Intel syntax, `as`, `ld`, Linux x86-64 syscalls, Docker/Compose, GitHub Actions, official Rinha 2026 resources.

---

## Evidence Baseline

- Official challenge repo inspected at `zanfranceschi/rinha-de-backend-2026` commit `d6296d9`.
- Existing C implementation inspected at `jonathanperis/rinha4-back-end-c` commit `619f0cc`; local `make test` passed.
- Existing standalone load balancer inspected at `jonathanperis/rinha4-lb-yolo-mode` commit `b5b0e37`; local `make clean test` passed.
- C candidate archive shows `p99=0.36ms`, `0 FP`, `0 FN`, `0 HTTP errors`, `final_score=6000` on GitHub Actions candidate benchmark.
- C official preview archive shows `p99=1.45ms`, `0 FP`, `0 FN`, `0 HTTP errors`, `final_score=5839.52`.

## Hard Gates

- Runtime implementation files must be assembly only: no C/Rust/Go/Zig/C#/Java implementation code.
- Final Compose must include one LB and at least two API instances.
- LB must not inspect `/fraud-score` payloads or generate fraud decisions.
- Total Compose limits must stay within `1 CPU / 350 MB`.
- Promote only candidates with `0 FP`, `0 FN`, and `0 HTTP errors`.
- Use immutable image tags before any official preview issue.

## Task 1: Bootstrap pure-assembly build and smoke API

**Objective:** Establish a buildable pure-assembly repo with a minimal direct TCP API for `/ready` and fixed `/fraud-score` smoke testing.

**Files:**
- Create: `Makefile`
- Create: `src/api/main.S`
- Create: `src/lb/main.S`
- Create: `tests/smoke_api.py`
- Create: `tests/check_purity.py`
- Create: `Dockerfile`
- Create: `info.json`

**Verification:**

```bash
make clean test
```

Expected:

```text
asm api smoke passed
purity check passed
```

## Task 2: Port fd-passing LB to assembly

**Objective:** Replace the LB scaffold with a working assembly equivalent of `rinha4-lb-yolo-mode` `LB_MODE=fdpass`.

**Files:**
- Modify: `src/lb/main.S`
- Create: `tests/integration_lb_fdpass.py`

**Implementation notes:**

- Use Linux syscalls directly: `socket`, `setsockopt`, `bind`, `listen`, `connect`, `accept4`, `sendmsg`, `close`, `nanosleep` if retrying upstream connection.
- Maintain persistent Unix control sockets to `/run/rinha/api1.sock` and `/run/rinha/api2.sock`.
- Round-robin accepted client FDs with `SCM_RIGHTS`.
- Do not read client payload bytes in the LB.

**Verification:**

```bash
make test-lb-fdpass
```

Expected: dummy API receivers get alternating client FDs and answer HTTP requests through inherited sockets.

## Task 3: Port API fdpass control plane to assembly

**Objective:** Replace direct TCP bootstrap mode with API control sockets that receive client FDs from the LB.

**Files:**
- Modify: `src/api/main.S`
- Create: `src/common/fdpass.S`
- Create: `src/common/net.S`
- Create: `tests/integration_api_fdpass.py`

**Implementation notes:**

- Listen on `API_FD_SOCK`, defaulting to `/run/rinha/api.sock` until env parsing exists.
- Receive FDs using `recvmsg` and `SCM_RIGHTS`.
- Process newly received FDs immediately, matching the C optimization proven by `tests/test_api_fdpass_immediate.c`.

## Task 4: Port manual HTTP parser and response table

**Objective:** Implement robust enough HTTP/1 request parsing for Rinha keep-alive or close semantics.

**Files:**
- Create: `src/common/http.S`
- Create: `src/common/responses.S`
- Modify: `src/api/main.S`

**Verification:**

- `GET /ready` returns `2xx`.
- `POST /fraud-score` returns one of six valid JSON response bodies.
- Unknown path returns 404.
- No HTTP 500 path exists for normal malformed requests.

## Task 5: Port vectorizer to assembly

**Objective:** Convert the C `vectorize.c` behavior to fixed-point x86-64 assembly.

**Files:**
- Create: `src/common/vectorize.S`
- Create: `tests/vectorize_vectors.json`
- Create: `tests/check_vectorize.py`

**Implementation notes:**

- Scan required JSON fields only; no generic parser.
- Preserve March 2026 timestamp fast path.
- Preserve `last_transaction: null` sentinel `-10000` for dimensions 5 and 6.
- Preserve MCC risk table and default `0.5`.
- Preserve `known_merchants` substring check semantics from the C implementation.

## Task 6: Port binary index loader and flat search

**Objective:** Load the existing C-format `index.bin` and perform exact flat search first for correctness.

**Files:**
- Create: `src/common/index.S`
- Create: `src/common/search.S`
- Create: `src/common/top5.S`
- Create: `tests/check_search.py`

**Verification:**

- Known sample vectors produce the same fraud counts as the C implementation.
- Exact search is allowed to be slow at this stage.

## Task 7: Port IVF/block8 search and repair policy

**Objective:** Match the current C repo search semantics and correctness policy.

**Files:**
- Modify: `src/common/search.S`
- Modify: `src/common/top5.S`

**Implementation notes:**

- Carry over `INDEX_NPROBE=3` and `INDEX_REPAIR_NPROBE=24` defaults.
- Carry over repair thresholds for fraud counts 0 and 5.
- Add AVX2 block8 distance scan after scalar correctness is proven.

## Task 8: Build the assembly index preprocessor

**Objective:** Generate the production `index.bin` without C implementation code.

**Files:**
- Create: `src/preprocess/build_index.S`
- Modify: `Dockerfile`
- Create: `tests/check_build_index.py`

**Implementation notes:**

- It is acceptable for the Docker build stage to use external `curl`/`gzip` tools as tools, but the repository-owned index converter must be assembly.
- Parse only the official `references.json` shape.
- Emit the same binary index format consumed by the runtime.

## Task 9: Add final Compose and submission branch workflow

**Objective:** Prepare final Rinha-compatible runtime layout.

**Files:**
- Create: `docker-compose.yml`
- Create: `.github/workflows/build.yml`
- Create: `.github/workflows/benchmark.yml`
- Create: `scripts/prepare-submission.sh`

**Compose target:**

- `lb`: `/app/lb`, port `9999`, `0.08 CPU / 30 MB` starting point.
- `api1`: `/app/api`, `/run/rinha/api1.sock`, `0.46 CPU / 160 MB`.
- `api2`: `/app/api`, `/run/rinha/api2.sock`, `0.46 CPU / 160 MB`.

## Task 10: Benchmark, tune, and official promotion

**Objective:** Run official-like CI comparisons and only promote stable winners.

**Verification:**

- Candidate benchmark: repeated runs, not single noisy result.
- Required result before official preview: `0 FP`, `0 FN`, `0 HTTP errors`.
- Official issue requires explicit user approval after promotion report.
