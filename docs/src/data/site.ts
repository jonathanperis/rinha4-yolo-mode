const rawBase = import.meta.env.BASE_URL;
export const base = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;

export const repoUrl = 'https://github.com/jonathanperis/rinha4-yolo-mode';
export const latestCiRun = 'https://github.com/jonathanperis/rinha4-yolo-mode/actions/workflows/ci.yml?query=branch%3Amain';
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
  ['lane.ci', 'main branch // smoke + purity checks'],
  ['lane.pages', 'main branch // github pages deploy'],
  ['runtime', 'fdpass // unix sockets // prebuilt responses'],
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
    status: '[CI-CLEAN]',
    label: 'GITHUB ACTIONS LANE',
    title: 'Main CI lane',
    stats: [
      ['SMOKE', 'pass'],
      ['PURITY', 'pass'],
      ['PAGES', 'live'],
    ],
    body: 'GitHub Actions evidence confirms main branch build, smoke test, purity check, release build and Pages deployment.',
    href: latestCiRun,
    cta: 'INSPECT RUN',
  },
];

export const sourceLinks = [
  { label: 'C REFERENCE PAGE', href: cReferenceUrl },
  { label: '.NET REFERENCE PAGE', href: dotnetReferenceUrl },
  { label: 'OFFICIAL CHALLENGE', href: challengeUrl },
];

export const localLinks = [
  { label: 'REPORT RUN', href: latestCiRun },
  { label: 'PAGES RUN', href: latestPagesRun },
  { label: 'SOURCE', href: repoUrl },
];

export const traceSteps = [
  ['01', 'Ingress', 'k6 / judge reaches :9999', 'The public boundary is the shared YOLO assembly load balancer.'],
  ['02', 'FD pass', 'SCM_RIGHTS over Unix sockets', 'Accepted client descriptors move to api1.sock and api2.sock without a second public TCP listener.'],
  ['03', 'Parse', 'manual HTTP + fraud fields', 'Assembly code reads only the bytes the workload needs for scoring and response selection.'],
  ['04', 'Score', 'heuristic branch-light path', 'The purity gate keeps shortcut decisions tied to request payload fields, not preview/test payload IDs.'],
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
    summary: 'The fd-passing topology, runtime service boundaries, and why the LB does not score requests.',
    intent: 'TRACE THE HOT PATH',
  },
  {
    slug: 'verification',
    title: 'Verification',
    summary: 'Local commands, CI workflows, compose validation, and the public runtime purity gate.',
    intent: 'VERIFY THE LANE',
  },
  {
    slug: 'benchmark-hygiene',
    title: 'Benchmark hygiene',
    summary: 'Image pinning, compose validation, artifact retention, and caveats before treating CI evidence as current.',
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
    ],
    checks: ['LB_MODE=fdpass', 'UPSTREAMS=/tmp/rinha/api1.sock,/tmp/rinha/api2.sock', 'No local /app/lb binary in this repo'],
  },
  verification: {
    title: 'Verification',
    kicker: 'PROOF LEDGER',
    body: [
      'The repo keeps a short verification loop for development and a heavier runtime purity when the official reference rules is available next to the workspace.',
      'CI mirrors this maturity loop. It assembles the API, runs smoke tests, checks purity, validates compose, builds an amd64 image, and can run an official-like benchmark manually.',
    ],
    checks: ['make clean test', 'python3 tests/check_purity.py', 'docker compose config --quiet'],
  },
  'benchmark-hygiene': {
    title: 'Benchmark hygiene',
    kicker: 'BENCHMARK STREAM',
    body: [
      'A credible repo-CI run needs immutable images, clean compose output, and retained artifacts for every repetition.',
      'Do not collapse one fast GitHub-hosted run into an official claim. Keep the 1 CPU / 350 MB envelope visible and report false positives, false negatives, and HTTP errors beside p99.',
    ],
    checks: ['Immutable image pin when benchmarking prebuilt code', 'docker compose config --quiet', '0 FP, 0 FN, 0 HTTP errors beside latency'],
  },
};
