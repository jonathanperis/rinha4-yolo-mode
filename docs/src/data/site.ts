const rawBase = import.meta.env.BASE_URL;
export const base = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;

export const nav = [
  { href: base, label: 'Workbench' },
  { href: `${base}docs/`, label: 'Docs' },
  { href: 'https://github.com/jonathanperis/rinha4-yolo-mode', label: 'GitHub' },
];

export const facts = [
  { label: 'Runtime', value: 'Pure x86-64 assembly API' },
  { label: 'LB default', value: 'Shared ASM fdpass load balancer' },
  { label: 'Topology', value: '1 LB, 2 API workers, Unix sockets' },
  { label: 'Resource split', value: '0.08 CPU LB, 0.46 CPU per API' },
];

export const evidence = [
  {
    claim: 'The repository-owned runtime implementation stays assembly-only.',
    source: 'tests/check_purity.py',
    detail: 'Purity check blocks non-assembly implementation files outside allowed docs, tests, and workflow areas.',
  },
  {
    claim: 'The API receives accepted client descriptors over Unix sockets.',
    source: 'docker-compose.yml',
    detail: 'API workers run /app/api with /tmp/rinha/api1.sock and /tmp/rinha/api2.sock.',
  },
  {
    claim: 'The load balancer default is the shared ASM fdpass image.',
    source: 'docker-compose.yml',
    detail: 'LB_MODE=fdpass, LB_FDPASS_SOCKET_TYPE=stream, LB_FDPASS_SNDBUF=262144.',
  },
  {
    claim: 'Local corpus replay has a zero-error target on the public corpus.',
    source: 'README.md',
    detail: 'Expected replay: 54100 total, 0 false positives, 0 false negatives, 0 HTTP errors, 0 score mismatches.',
  },
];

export const docs = [
  {
    slug: 'architecture',
    title: 'Architecture',
    summary: 'The fd-passing topology, runtime service boundaries, and why the LB does not score requests.',
    intent: 'Understand the system shape',
  },
  {
    slug: 'verification',
    title: 'Verification',
    summary: 'Local commands, CI workflows, compose validation, and the public corpus replay gate.',
    intent: 'Prove it works locally',
  },
  {
    slug: 'submission',
    title: 'Submission readiness',
    summary: 'Image pinning, branch hygiene, official issue constraints, and benchmark promotion rules.',
    intent: 'Prepare a contest run',
  },
];

export const pages = {
  architecture: {
    title: 'Architecture',
    kicker: 'fd-passing workbench',
    body: [
      'The runtime is intentionally small. A shared assembly load balancer accepts public TCP traffic on port 9999, chooses an API worker, and transfers the accepted client file descriptor over a Unix socket using SCM_RIGHTS.',
      'The API workers are the scoring boundary. They parse HTTP and JSON directly from inherited client descriptors, then respond on the same descriptor. The load balancer only routes descriptors and never inspects fraud payloads.',
    ],
    checks: ['LB_MODE=fdpass', 'UPSTREAMS=/tmp/rinha/api1.sock,/tmp/rinha/api2.sock', 'No local /app/lb binary in this repo'],
  },
  verification: {
    title: 'Verification',
    kicker: 'local proof rail',
    body: [
      'The repo keeps a short verification loop for development and a heavier corpus replay when the official public dataset is available next to the workspace.',
      'CI mirrors this maturity loop. It assembles the API, runs smoke tests, checks purity, validates compose, builds an amd64 image, and can run an official-like benchmark manually.',
    ],
    checks: ['make clean test', 'make corpus-replay', 'docker compose config --quiet'],
  },
  submission: {
    title: 'Submission readiness',
    kicker: 'promotion guardrails',
    body: [
      'A mature candidate needs immutable images, clean compose output, and repeated benchmark evidence. The official Rinha issue flow should use the registered participant id only after the submission branch is verified.',
      'Promotion is not a single fast run. The participant must stay within the 1 CPU and 350 MB envelope, avoid build directives in submission compose, and report zero false positives, false negatives, and HTTP errors.',
    ],
    checks: ['No build directives on submission branch', 'No latest tags or image fallbacks', '0 FP, 0 FN, 0 HTTP errors before promotion'],
  },
};
