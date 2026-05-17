const rawBase = import.meta.env.BASE_URL;
export const base = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;

export const repoUrl = 'https://github.com/jonathanperis/rinha4-yolo-mode';
export const latestCiRun = 'https://github.com/jonathanperis/rinha4-yolo-mode/actions/workflows/ci.yml?query=branch%3Amain';
export const latestPagesRun = 'https://github.com/jonathanperis/rinha4-yolo-mode/actions/workflows/pages.yml?query=branch%3Amain';
export const latestBuildRun = 'https://github.com/jonathanperis/rinha4-yolo-mode/actions/workflows/build.yml?query=branch%3Amain';
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
  { label: '[corpus]', value: '54100 clean' },
  { label: '[fdpass]', value: 'stream sockets' },
];

export const consoleLines = [
  ['lane.asm_runtime', 'pure assembly api // _start // as + ld'],
  ['lane.corpus_replay', '54100 total // 0 fp // 0 fn // 0 http errors'],
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
    status: '[CORPUS-CLEAN]',
    label: 'LOCAL REPLAY LANE',
    title: '54100 cases',
    stats: [
      ['FP', '0'],
      ['FN', '0'],
      ['HTTP', '0'],
    ],
    body: 'Public corpus replay target is zero false positives, zero false negatives, zero HTTP errors, and zero score mismatches.',
    href: `${repoUrl}/blob/main/tests/corpus_replay.py`,
    cta: 'INSPECT REPLAY',
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
    body: 'GitHub Actions evidence confirms main branch build, smoke test, purity check, release build, CodeQL, and Pages deployment.',
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
  ['04', 'Score', 'corpus table + branch-light path', 'The replay gate keeps shortcut decisions tied to the public corpus and score expectations.'],
  ['05', 'Respond', 'prebuilt HTTP bytes out', 'Workers write prepared response bytes back on the inherited client descriptor.'],
];

export const abLanes = [
  {
    key: 'evidence',
    title: 'Evidence Terminal',
    body: 'Default lane. Lead with assembly runtime, corpus replay, CI status, and caveats above the fold.',
    href: `${base}?ab=evidence`,
  },
  {
    key: 'ledger',
    title: 'Benchmark Ledger',
    body: 'Make provenance the lead object: source, run, compose, replay, workflow, and Pages deployment.',
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
    summary: 'Local commands, CI workflows, compose validation, and the public corpus replay gate.',
    intent: 'VERIFY THE LANE',
  },
  {
    slug: 'submission',
    title: 'Submission readiness',
    summary: 'Image pinning, branch hygiene, official issue constraints, and benchmark promotion rules.',
    intent: 'PREPARE A RUN',
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
      'The repo keeps a short verification loop for development and a heavier corpus replay when the official public dataset is available next to the workspace.',
      'CI mirrors this maturity loop. It assembles the API, runs smoke tests, checks purity, validates compose, builds an amd64 image, and can run an official-like benchmark manually.',
    ],
    checks: ['make clean test', 'make corpus-replay', 'docker compose config --quiet'],
  },
  submission: {
    title: 'Submission readiness',
    kicker: 'BENCHMARK STREAM',
    body: [
      'A mature candidate needs immutable images, clean compose output, and repeated benchmark evidence. The official Rinha issue flow should use the registered participant id only after the submission branch is verified.',
      'Promotion is not a single fast run. The participant must stay within the 1 CPU and 350 MB envelope, avoid build directives in submission compose, and report zero false positives, false negatives, and HTTP errors.',
    ],
    checks: ['No build directives on submission branch', 'No latest tags or image fallbacks', '0 FP, 0 FN, 0 HTTP errors before promotion'],
  },
};
