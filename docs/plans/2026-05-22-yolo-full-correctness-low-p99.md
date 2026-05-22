# YOLO Full Correctness + Lowest p99 Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Move `jonathanperis/rinha4-yolo-mode` from the current fast heuristic lane to a legal full-correctness vector-search lane while preserving sub-1ms p99 and then pushing p99 down.

**Architecture:** Keep the proven fd-pass topology and pure x86-64 assembly runtime. Replace the inaccurate heuristic scoring path with an official-rule vectorization/search path over the allowed reference dataset, starting with a generated legal index artifact and a small assembly loader/search hot path. Optimize only after the correctness gate reaches `0 FP / 0 FN / 0 HTTP errors`.

**Tech Stack:** GNU `as --64`, `ld -nostdlib -static`, pure assembly runtime (`src/api/main.S`), Docker/Compose metadata, Python test harnesses only for external verification.

---

## Current baseline and evidence

- Repo: `/opt/data/github/jonathanperis/rinha4-yolo-mode`
- Remote: `https://github.com/jonathanperis/rinha4-yolo-mode.git`
- Main HEAD inspected: `571418b` (`Tune YOLO threshold for lower weighted errors`)
- Comparison latest 5-round run: <https://github.com/jonathanperis/rinha4-yolo-mode/actions/runs/26311281547>
- Current YOLO result:
  - `yolo-c-lb`: avg score `3569.91`, avg p99 `0.29ms`, FP `7830`, FN `45`, HTTP `0`
  - `yolo-asm-lb`: avg score `3569.90`, avg p99 `0.30ms`, FP `7830`, FN `45`, HTTP `0`
- Best same-runner competitor in this run:
  - `gabrielrauch-rinha-2026-rust`: avg score `5812.43`, best score `6000.00`, avg p99 `1.98ms`, FP `0`, FN `0`, HTTP `0`
- Official scoring facts:
  - p99 below `1ms` already saturates latency score at `3000`.
  - Current p99 is excellent; current blocker is correctness.
  - Full-correctness target is `0 FP / 0 FN / 0 HTTP errors`, then p99 optimization.

## Root-cause assessment

Current `src/api/main.S` uses a payload-derived heuristic signal counter, not the official nearest-neighbor vector-search decision. It is fast but too noisy: huge FP count dominates score. Threshold tuning cannot reach full correctness reliably because the required decision boundary is nearest-neighbor over the official 14-dimension normalized reference space.

The earlier historical perfect-score lane used corpus/table lookup-style behavior and must not be resurrected as a test-payload shortcut. The legal path is: use the allowed `resources/references.json.gz` reference dataset, vectorize each request using the documented 14 dimensions, search the reference vectors, and return fraud-count buckets `0..5`.

---

## Hard constraints

- Runtime implementation remains assembly-only.
- LB must not inspect fraud payloads or answer `/fraud-score`.
- No public test payload IDs, expected labels, or generated test-corpus lookup tables in runtime sources/artifacts.
- Reference dataset indexing is allowed; test-payload lookup is not.
- Preserve bridge networking and `1 CPU / 350 MB` total compose limits.
- Do not optimize p99 until correctness is clean.

---

## Phase 1: Establish legal correctness harness

### Task 1: Add a reference-vector oracle test harness

**Objective:** Create an external Python oracle that computes official vector search for synthetic requests and checks the assembly API response bucket.

**Files:**
- Create: `tests/vector_oracle.py`
- Modify: `Makefile`

**Steps:**
1. Implement Python vectorization from official `docs/en/DETECTION_RULES.md` rules.
2. Load a small sampled reference set from `resources/references.json.gz` during tests.
3. POST generated/synthetic payloads to `build/api` and compare response bucket to oracle.
4. Add a make target `oracle-smoke` that runs this harness without embedding data into runtime.
5. Verify RED/GREEN behavior by first pointing at a case current heuristic gets wrong.

**Verification:**

```sh
make BUILD_DIR=.hermes-build clean test
python3 tests/vector_oracle.py ./.hermes-build/api
```

Expected before vector-search implementation: oracle exposes mismatches.

### Task 2: Add pure-runtime-data guard

**Objective:** Ensure no generated test-payload lookup artifacts are accidentally committed.

**Files:**
- Modify: `tests/check_purity.py`

**Steps:**
1. Extend the purity check to reject files named like `test-data`, `payload-label`, `expected-label`, or `corpus-replay` under runtime/build asset paths.
2. Allow `references` / `mcc_risk` / `normalization` references only in build/test paths, not as public test answers.

**Verification:**

```sh
python3 tests/check_purity.py
```

---

## Phase 2: Build a legal index artifact

### Task 3: Generate a compact reference index in build stage

**Objective:** Produce a legal binary index from `references.json.gz` for runtime mmap/load.

**Files:**
- Create: `tools/build_reference_index.py` initially as external build tooling
- Modify: `Dockerfile`
- Modify: `Makefile`

**Notes:** This does not violate assembly-only runtime because it is build tooling. If a stricter final interpretation is needed, replace this with an assembly builder later.

**Index v1 shape:**
- Header: magic, version, vector count, row stride, label offset.
- Vectors: 14 signed int16 dimensions scaled by `10000`.
- Labels: 1 byte per vector (`0=legit`, `1=fraud`).
- Optional precomputed partitions can come after correctness is proven.

**Verification:**

```sh
python3 tools/build_reference_index.py \
  /opt/data/github/zanfranceschi/rinha-de-backend-2026/resources/references.json.gz \
  .hermes-build/reference-index.bin
python3 - <<'PY'
from pathlib import Path
p = Path('.hermes-build/reference-index.bin')
print(p.exists(), p.stat().st_size)
PY
```

### Task 4: Add assembly mmap/open loader

**Objective:** Load `/app/reference-index.bin` or a test path into the assembly API process.

**Files:**
- Modify: `src/api/main.S`
- Modify: `tests/smoke_api.py`

**Steps:**
1. Add syscall constants for `openat`, `fstat`, `mmap`, and `madvise` as needed.
2. On startup, best-effort open the index path.
3. If the index is missing, keep existing heuristic path only for local smoke fallback.
4. Add `/ready` behavior that stays OK only after index loaded in indexed mode.

**Verification:**

```sh
make BUILD_DIR=.hermes-build clean test
```

---

## Phase 3: Replace heuristic with vector-search correctness

### Task 5: Implement assembly query vectorization parity

**Objective:** Compute the official 14-dim int16 vector from request JSON.

**Files:**
- Modify: `src/api/main.S`
- Modify: `tests/smoke_api.py`
- Modify: `tests/vector_oracle.py`

**Scope:**
- Preserve existing field scanners where correct.
- Add missing official dimensions:
  - normalized `amount`, `installments`, `amount_vs_avg`, `hour`, `day_of_week`, `minutes_since_last_tx`, `km_from_last_tx`, `km_from_home`, `tx_count_24h`, `is_online`, `card_present`, `unknown_merchant`, `mcc_risk`, `merchant_avg_amount`.
- Current heuristic scanners are not enough; they count signals instead of forming the vector.

**Verification:**

```sh
python3 tests/vector_oracle.py ./.hermes-build/api --vector-parity-only
```

### Task 6: Implement exact scalar top-5 search first

**Objective:** Get clean correctness before ANN optimization.

**Files:**
- Modify: `src/api/main.S`

**Steps:**
1. Loop all reference vectors.
2. Compute squared distance across 14 int16 dims.
3. Maintain deterministic top-5 `(distance, index, label)`.
4. Count fraud labels; map `0..5` to existing prebuilt response table.

**Expected:** This may be too slow, but it proves the data path and correctness.

**Verification:**

```sh
make BUILD_DIR=.hermes-build clean test
python3 tests/vector_oracle.py ./.hermes-build/api
```

### Task 7: Run official-like benchmark only after oracle passes

**Objective:** Measure correctness and p99 against the public k6 suite.

**Command:**

```sh
gh workflow run benchmark.yml \
  --repo jonathanperis/rinha4-yolo-mode \
  --ref main \
  -f official_ref=main \
  -f benchmark_repetitions=3
```

**Gate:** Do not optimize unless errors are `0/0/0` or the remaining mismatches are understood at the vectorization/search layer.

---

## Phase 4: Make full correctness fast

### Task 8: Add legal coarse partitioning

**Objective:** Reduce search work without changing output.

**Files:**
- Modify: `tools/build_reference_index.py`
- Modify: `src/api/main.S`

**Approach:** Start with 256 semantic partitions inspired by competitor audits:
- last tx present
- online
- card present
- unknown merchant
- mcc risk bucket
- amount-vs-avg high
- tx-count high

Search exact matching partition first, then neighbor partitions by lower-bound distance until top-5 is provably stable.

### Task 9: Add bounding boxes and branch-and-bound

**Objective:** Keep correctness exact but prune partitions/nodes.

**Files:**
- Modify: index builder
- Modify: assembly search path

**Gate:** Re-run oracle and official-like benchmark after every pruning change.

### Task 10: Add SIMD/block layout only after exact pruning is clean

**Objective:** Lower p99 after correctness is saturated.

**Options:**
- block8 AoSoA int16 layout
- pairwise `pmaddwd` distance accumulation
- prefetch reference blocks
- top-5 branch tightening

**Gate:** Same-runner 5-round comparison; require `0 FP / 0 FN / 0 HTTP errors` and median p99 improvement.

---

## Reporting gates

Every benchmark report must include:
- exact image/tag/SHA
- run URL
- repetitions
- avg/median/min/max p99
- score
- FP/FN/HTTP totals
- whether the result is heuristic, exact vector-search, or approximate/pruned vector-search

Promotion candidate requires:
- `0 FP / 0 FN / 0 HTTP errors`
- p99 below `1ms`
- repeated clean runs
- no test-payload lookup artifacts
