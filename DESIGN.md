# DESIGN.md: rinha4-yolo-mode Pages

_Last updated: 2026-05-17_

## Design intent

Create a source-backed architecture workbench for a pure-assembly benchmark participant. The result should keep the same dark, technical, competition-oriented aesthetic already implied by the repo, but feel more intentional: quiet grid, precise labels, inspectable topology, and proof rows instead of decorative neon.

## Physical scene

A systems engineer is reviewing a contest participant late at night on a large monitor, switching between GitHub, compose files, and benchmark logs. The interface should be dark, legible, and calm because it is used for inspection, not celebration.

## Register

brand

## Aesthetic anchors to preserve

- Dark operator surface.
- Monospace accents for commands, paths, and service labels.
- Cyan and green accents for transport and verification state.
- Technical density, but with clear reading order.

## Color strategy

Restrained dark workbench with two active accents. Use OKLCH tokens and tinted neutrals, never pure black or pure white.

```css
--ink-950: oklch(0.145 0.015 230);
--ink-900: oklch(0.18 0.018 230);
--ink-800: oklch(0.24 0.022 230);
--paper-100: oklch(0.93 0.012 220);
--paper-300: oklch(0.78 0.018 225);
--muted-500: oklch(0.58 0.028 225);
--cyan-400: oklch(0.74 0.15 205);
--green-400: oklch(0.77 0.14 155);
--amber-400: oklch(0.78 0.14 75);
--red-400: oklch(0.68 0.18 30);
```

## Typography

- One sans family for prose and interface labels, system stack for reliability.
- Mono only for commands, file paths, service names, and small diagnostic labels.
- Large headings use tight line height and clear scale contrast.
- Body line length should stay under `72ch`.

## Layout principles

- Root page is a workbench, not a centered marketing stack.
- First viewport should answer: what is this, how is it wired, how do I verify it?
- `/docs/` is a command center, not a dumped README.
- Use different module shapes for topology, evidence, and docs routes. Avoid repeated identical cards.
- Internal links must respect the GitHub Pages base path `/rinha4-yolo-mode/`.

## Component direction

- **Hero:** proof-led title, compact status rail, docs/source CTAs, and variant controls.
- **Topology panel:** semantic diagram with LB, Unix sockets, API workers, and direct fd response path.
- **Evidence ledger:** rows that bind a claim to a file, command, or workflow.
- **Docs command center:** route cards grouped by reader intent: understand, verify, submit.
- **Command panels:** copyable-looking snippets with real commands.
- **Status chips:** small text labels, full borders, no side-stripe accents.

## A/B variants

The shipped static site supports query-based review variants:

- `?ab=control`: default docs-first flow.
- `?ab=proof`: hero emphasizes verification and corpus replay.
- `?ab=architecture`: hero emphasizes fd-passing topology.

## Accessibility

- Minimum readable contrast on dark backgrounds.
- Visible keyboard focus rings.
- No content hidden behind hover only interactions.
- Respect `prefers-reduced-motion`.
- Use semantic headings and landmark elements.
- Keep docs cards and tables usable at narrow widths.

## Motion

Use limited reveal motion only where it clarifies hierarchy. No animated layout properties, no bouncing, no constant glow loops. Disable decorative motion for reduced-motion users.

## Copy standards

- Every claim should be tied to source, command, or workflow evidence.
- Use exact filenames and service names.
- Avoid em dashes in prose.
- Avoid exaggerated speed language unless paired with benchmark context.

## Quality gates

- `bun install --frozen-lockfile` from `docs/`.
- `bun run build` from `docs/`.
- `make clean test` from repo root.
- `docker compose config --quiet` from repo root.
- Smoke local preview for `/rinha4-yolo-mode/`, `/rinha4-yolo-mode/docs/`, and each A/B query.
- Verify live GitHub Pages after merge and deployment.
