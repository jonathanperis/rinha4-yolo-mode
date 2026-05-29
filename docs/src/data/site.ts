const rawBase = import.meta.env.BASE_URL;
export const base = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;

export const repoUrl = 'https://github.com/jonathanperis/rinha4-yolo-mode';
export const latestCiRun = 'https://github.com/jonathanperis/rinha4-yolo-mode/actions/workflows/ci.yml?query=branch%3Amain';
export const latestBuildRun = 'https://github.com/jonathanperis/rinha4-yolo-mode/actions/workflows/build.yml?query=branch%3Amain';
export const latestBenchmarkRun = 'https://github.com/jonathanperis/rinha4-yolo-mode/actions/workflows/benchmark.yml?query=branch%3Amain';
export const latestPagesRun = 'https://github.com/jonathanperis/rinha4-yolo-mode/actions/workflows/pages.yml?query=branch%3Amain';
export const challengeUrl = 'https://github.com/zanfranceschi/rinha-de-backend-2026';
export const cReferenceUrl = 'https://jonathanperis.github.io/rinha4-back-end-c/';
export const dotnetReferenceUrl = 'https://jonathanperis.github.io/rinha4-back-end-dotnet/';

export const nav = [
  { href: `${base}docs/`, label: 'DOCS' },
  { href: latestCiRun, label: 'REPORTS' },
  { href: repoUrl, label: 'GITHUB' },
];

export const heroTags = [
  { label: '[asm]', value: 'pure x86-64' },
  { label: '[purity]', value: 'no lookup' },
  { label: '[fdpass]', value: 'stream sockets' },
];

export const consoleLines = [
  ['lane.asm_runtime', 'pure assembly api // _start // as + ld'],
  ['lane.runtime_purity', 'no test-payload lookup tables'],
  ['lane.ci', 'main branch // smoke + purity + compose'],
  ['lane.oracle', 'optional vector oracle // black-box calibration'],
  ['lane.pages', 'main branch // github pages deploy'],
  ['runtime', 'fdpass // unix sockets // inherited client fds'],
  ['topology', 'asm_lb:9999 -> api[2] over /tmp/rinha/*.sock'],
  ['caveat', 'ci numbers are evidence, not official hardware'],
];

export const proofCards = [
  {
    status: '[ASM-RUNTIME]',
    label: 'IMPLEMENTATION LANE',
    title: 'Pure assembly API',
    stats: [
      ['ENTRY', '_start'],
      ['BUILD', 'as + ld'],
      ['CHECK', 'purity pass'],
    ],
    body: 'Repository-owned runtime implementation stays assembly-only. Tests block non-assembly implementation drift.',
    href: `${repoUrl}/blob/main/tests/check_purity.py`,
    cta: 'OPEN PURITY CHECK',
  },
  {
    status: '[PURITY-CLEAN]',
    label: 'RUNTIME PURITY LANE',
    title: 'No lookup tables',
    stats: [
      ['PAYLOAD', 'field-derived'],
      ['LOOKUP', 'blocked'],
      ['ASM', 'only'],
    ],
    body: 'Runtime purity target is zero preview/test-payload lookup artifacts in shipped assembly sources.',
    href: `${repoUrl}/blob/main/tests/check_purity.py`,
    cta: 'INSPECT PURITY',
  },
  {
    status: '[ORACLE-SMOKE]',
    label: 'CALIBRATION LANE',
    title: 'Vector oracle is optional',
    stats: [
      ['TARGET', 'make oracle-smoke'],
      ['SOURCE', 'official resources'],
      ['RULE', 'black-box only'],
    ],
    body: 'The vector oracle exercises reference payloads as an external smoke gate without generating runtime lookup artifacts.',
    href: `${repoUrl}/blob/main/tests/vector_oracle.py`,
    cta: 'OPEN ORACLE',
  },
  {
    status: '[CI-CLEAN]',
    label: 'GITHUB ACTIONS LANE',
    title: 'Main CI and release lanes',
    stats: [
      ['SMOKE', 'pass'],
      ['PURITY', 'pass'],
      ['RELEASE', 'separate'],
    ],
    body: 'CI proves smoke, fd-pass keepalive, purity, and compose validation. Build and Release is a separate lane for amd64 images and semantic tags.',
    href: latestCiRun,
    cta: 'INSPECT CI',
  },
];

export const sourceLinks = [
  { label: 'C REFERENCE PAGE', href: cReferenceUrl },
  { label: '.NET REFERENCE PAGE', href: dotnetReferenceUrl },
  { label: 'OFFICIAL CHALLENGE', href: challengeUrl },
];

export const localLinks = [
  { label: 'CI RUN', href: latestCiRun },
  { label: 'BUILD/RELEASE RUN', href: latestBuildRun },
  { label: 'BENCHMARK RUN', href: latestBenchmarkRun },
  { label: 'PAGES RUN', href: latestPagesRun },
  { label: 'SOURCE', href: repoUrl },
];

export const traceSteps = [
  ['01', 'Ingress', 'k6 / judge reaches :9999', 'The public boundary is the shared YOLO assembly load balancer.'],
  ['02', 'FD pass', 'SCM_RIGHTS over Unix sockets', 'Accepted client descriptors move to api1.sock and api2.sock without a second public TCP listener.'],
  ['03', 'Parse', 'manual HTTP + fraud fields', 'Assembly code reads only the bytes the workload needs for scoring and response selection.'],
  ['04', 'Score', 'heuristic branch-light path', 'Payload fields feed amount, velocity, MCC, merchant, geo, online, and card-present risk buckets.'],
  ['05', 'Respond', 'prebuilt HTTP bytes out', 'Workers write prepared response bytes back on the inherited client descriptor.'],
];

export const abLanes = [
  {
    key: 'evidence',
    title: 'Evidence Terminal',
    body: 'Default lane. Lead with assembly runtime, runtime purity, CI status, and caveats above the fold.',
    href: `${base}?ab=evidence`,
  },
  {
    key: 'ledger',
    title: 'Benchmark Ledger',
    body: 'Make provenance the lead object: source, run, compose, purity, workflow, and Pages deployment.',
    href: `${base}?ab=ledger`,
  },
  {
    key: 'runtime',
    title: 'Runtime Trace',
    body: 'Lead with architecture: load balancer, fd pass, parser, scorer, and bytes written back.',
    href: `${base}?ab=runtime`,
  },
];

export const docs = [
  {
    slug: 'architecture',
    title: 'Architecture',
    summary: 'The fd-passing topology, compose resource split, runtime service boundaries, and why the LB does not score requests.',
    intent: 'TRACE THE HOT PATH',
  },
  {
    slug: 'verification',
    title: 'Verification',
    summary: 'Local smoke, fd-pass keepalive, purity, optional vector oracle, compose validation, and CI lanes.',
    intent: 'VERIFY THE LANE',
  },
  {
    slug: 'official-evaluation',
    title: 'Official evaluation gate',
    summary: 'Manual official-like k6 workflow defaults, inputs, artifacts, scoring facts, and black-box use constraints.',
    intent: 'CALIBRATE WITHOUT OVERCLAIMING',
  },
  {
    slug: 'benchmark-hygiene',
    title: 'Benchmark hygiene',
    summary: 'Image pinning, compose validation, artifact retention, release tags, and caveats before treating CI evidence as current.',
    intent: 'KEEP RUNS REPRODUCIBLE',
  },
];

export const pages = {
  architecture: {
    title: 'Architecture',
    kicker: 'RUNTIME TRACE',
    body: [
      'The runtime is intentionally small. A shared assembly load balancer accepts public TCP traffic on port 9999, chooses an API worker, and transfers the accepted client file descriptor over a Unix socket using SCM_RIGHTS.',
      'The API workers are the scoring boundary. They parse HTTP and fraud fields directly from inherited client descriptors, then respond on the same descriptor. The load balancer only routes descriptors and never inspects fraud payloads.',
      'Compose keeps the contest envelope explicit: LB 0.06 CPU / 30M, api1 0.47 CPU / 160M, and api2 0.47 CPU / 160M. The LB runs in fdpass stream mode with a 262144 send buffer and two upstream Unix sockets.',
      'The heuristic is source-backed rather than corpus-backed. It considers amount, installments, customer velocity, amount ratios, MCC risk, known merchant state, online/card-present hints, and distance fields, then maps the capped fraud count into public buckets 0.0, 0.2, 0.4, 0.6, or 1.0.',
    ],
    checks: [
      'LB_MODE=fdpass; LB_FDPASS_SOCKET_TYPE=stream; LB_FDPASS_SNDBUF=262144',
      'UPSTREAMS=/tmp/rinha/api1.sock,/tmp/rinha/api2.sock',
      'Compose BACKLOG=65535 for the shared LB; direct assembly TCP smoke uses BACKLOG=4096',
      'Resource split: LB 0.06 CPU / 30M; API workers 0.47 CPU / 160M each',
      'No local /app/lb binary and no LB fraud scoring in this repo',
    ],
  },
  verification: {
    title: 'Verification',
    kicker: 'PROOF LEDGER',
    body: [
      'The normal local gate is make clean test: assemble the API, run direct TCP smoke, run fd-pass keepalive smoke, and reject runtime lookup artifacts with tests/check_purity.py.',
      'make oracle-smoke is optional and heavier. It runs tests/vector_oracle.py against official reference resources as a black-box calibration smoke; it must not generate payload-ID, expected-label, or lookup artifacts for runtime code.',
      'CI mirrors the mandatory lane by running make clean test and docker compose config --quiet. The test target also runs a source-backed docs drift check for resource split, backlog, oracle, benchmark, and release-tag claims. Build and Release repeats the tests before publishing amd64 images, while Pages deploys this static dossier.',
    ],
    checks: [
      'make clean test',
      'make oracle-smoke  # optional when official reference resources are available',
      'python3 tests/check_docs_drift.py',
      'python3 tests/check_purity.py',
      'docker compose config --quiet',
      'CI workflow: smoke + fdpass + purity + compose validation',
    ],
  },
  'official-evaluation': {
    title: 'Official evaluation gate',
    kicker: 'PUBLIC K6 CALIBRATION',
    body: [
      'The manual Official-like Benchmark workflow and scripts/ci-official-benchmark.sh use zanfranceschi/rinha-de-backend-2026 at official_ref/OFFICIAL_REF=main by default. Older refs are only for explicitly labeled historical reproduction.',
      'The workflow accepts official_ref, webapi_image, and benchmark_repetitions. The local script mirrors those as OFFICIAL_REF, WEBAPI_IMAGE, and BENCHMARK_REPETITIONS, with RESULTS_DIR defaulting to benchmark-results and BENCHMARK_K6_MODE fixed to native.',
      'Artifacts are retained for audit: selected results.json, results-repetition-*.json, repetition-summary.json for multi-run selection, k6-output and k6-report files, docker-compose.log, and docker-state snapshots before/after repetitions.',
      'This is a rejection and calibration gate, not an official score claim. The public evaluator is used only as a black-box harness; payloads, expected labels, and derived lookup tables must not enter shipped runtime sources.',
    ],
    checks: [
      'workflow_dispatch input official_ref defaults to main',
      'workflow_dispatch input webapi_image may pin a prebuilt API image',
      'workflow_dispatch input benchmark_repetitions controls repeated k6 runs',
      'scripts/ci-official-benchmark.sh emits results.json and repetition artifacts',
      'docs/official-evaluation.md records scoring thresholds and rule caveats',
    ],
  },
  'benchmark-hygiene': {
    title: 'Benchmark hygiene',
    kicker: 'BENCHMARK STREAM',
    body: [
      'A credible repo-CI run needs immutable images, clean compose output, and retained artifacts for every repetition. Treat GitHub-hosted runs as evidence with provenance, not as final official hardware.',
      'Build and Release publishes exact tag families on non-PR runs: latest on the default branch, semantic v<major>.<minor>.<patch> release tags on main, immutable ci-<full-sha>, and Docker metadata sha-* tags. Docs-only changes intentionally skip that workflow unless manually dispatched.',
      'Keep the 1 CPU / 350 MB envelope visible and report false positives, false negatives, and HTTP errors beside p99. The public scoring model heavily penalizes HTTP errors and high detection error rates.',
    ],
    checks: [
      'Immutable image pin when benchmarking prebuilt code',
      'docker compose config --quiet',
      '0 FP, 0 FN, 0 HTTP errors beside latency',
      'GHCR tags: latest, vX.Y.Z, ci-<sha>, sha-*',
      'Build and Release paths-ignore docs/**',
    ],
  },
};
