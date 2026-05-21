# DESIGN.md: rinha4-yolo-mode Pages

_Last updated: 2026-05-17_

## Design intent

Recast `rinha4-yolo-mode` as a direct visual variant of the existing C and .NET Rinha4 Pages. Preserve the family system: CRT terminal surface, monospace, glitch headline, proof ledger, benchmark console, runtime trace, report CTAs, and lane-labeled caveats. The difference is content and accent: assembly/YOLO should feel more phosphor, more register-level, and more explicit about experimental evidence.

## Physical scene

A systems engineer is comparing the C, .NET, and assembly candidates on a dim monitor after a benchmark run. They need to see official, CI, and local evidence as separate lanes before trusting any claim.

## Register

brand

## Reference grammar to inherit

- Header: bullet logo, uppercase `DOCS`, `REPORTS`, `GITHUB`.
- Hero: split layout, giant glitch/CRT headline, boxed copy, small lane tags, benchmark console on the right.
- Sections: `PROOF LEDGER`, `OFFICIAL SOURCE`, `RUNTIME TRACE`, `A/B TEST SURFACE`, `CI BENCHMARK STREAM`.
- Components: lane cards, evidence strips, terminal transcript, trace rows, rectangular buttons, no rounded SaaS cards.
- Copy: short uppercase headings, provenance caveats, operational CTAs.

## Color strategy

Committed CRT dark. The family palette is black-green with amber and red proof accents. The assembly variant adds hotter phosphor green and caution amber while keeping red for primary verification actions.

```css
--crt-bg: oklch(0.13 0.03 155);
--crt-bg-2: oklch(0.17 0.035 155);
--crt-panel: oklch(0.22 0.04 155);
--crt-panel-2: oklch(0.27 0.045 155);
--crt-text: oklch(0.88 0.035 150);
--crt-muted: oklch(0.68 0.04 150);
--phosphor: oklch(0.82 0.22 142);
--amber: oklch(0.82 0.16 82);
--danger: oklch(0.68 0.24 18);
--calibration: oklch(0.68 0.16 270);
```

## Typography

- Monospace is intentional here because the reference family is a benchmark terminal.
- Use one system monospace stack.
- Headings are uppercase and compressed by size, tracking, and shadow instead of gradient text.
- Body copy stays readable with larger line-height and limited width.

## Layout principles

- Root page follows proof, provenance, mechanism, and telemetry.
- The first viewport must look related to the C and .NET pages.
- `/docs/` remains a command center, but it should share the same terminal family styling.
- Use lane labels instead of generic feature cards.
- Internal links must respect `/rinha4-yolo-mode/`.

## Component direction

- **Hero:** `YOLO SIGNAL UNDER LOAD`, proof tags, CTAs, right-side benchmark console.
- **Proof ledger:** three lane cards: assembly runtime, runtime purity, CI/deploy status.
- **Source strip:** split official/reference source from local YOLO evidence.
- **Runtime trace:** five rows: ingress, fd pass, parse, score, respond.
- **A/B surface:** `evidence`, `ledger`, `runtime` query variants.
- **CI stream:** latest run IDs and workflow states as evidence, not official hardware.

## Accessibility

- Text contrast must remain readable despite CRT texture.
- `prefers-reduced-motion` disables flicker and hover lifts.
- Buttons and lane cards need visible focus rings.
- Color is never the only status marker. Bracket labels carry state text.
- Docs routes must keep one `h1` per page and semantic landmarks.

## Quality gates

- `bun install --frozen-lockfile` from `docs/`.
- `bun run build` from `docs/`.
- `make clean test` from repo root.
- `docker compose config --quiet` from repo root.
- Smoke `/rinha4-yolo-mode/`, `/docs/`, `/docs/architecture/`, `/docs/verification/`, and A/B query URLs.
- Visual check against the C and .NET reference family.
- Verify live GitHub Pages after merge and deployment.
