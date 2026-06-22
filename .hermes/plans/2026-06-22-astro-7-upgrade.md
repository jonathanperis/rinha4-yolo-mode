# Astro 7 upgrade plan

## Scope

Upgrade only the GitHub Pages proof-dossier app under `docs/`. The Rinha runtime, compose topology, benchmark scripts, and assembly sources stay untouched.

## Repo fit against Astro 7 features

- **Adopt now:** Astro 7/Vite 8/Rolldown dependency refresh for faster builds and stricter compiler validation.
- **Adopt now:** `@astrojs/markdown-satteri` 0.3.x, because this repo already uses Sätteri in `astro.config.mjs` for Markdown processing.
- **Adopt now:** managed background dev-server scripts for agent-friendly local docs work (`dev:background`, `dev:logs`, `dev:stop`).
- **Keep existing:** static GitHub Pages deployment with Node 24 before Bun.
- **Skip for now:** route caching, CDN cache providers, and `src/fetch.ts` advanced routing; this site is `output: 'static'` on GitHub Pages and has no SSR request pipeline or CDN cache provider to configure.
- **Skip for now:** custom logger config; Astro 7 exposes `--json` globally when needed, but the repo does not run a long-lived Astro service in production.

## Implementation steps

1. Refresh `docs/package.json` and `docs/bun.lock` to Astro 7 and Sätteri 0.3.x.
2. Add package scripts for Astro 7 background dev-server lifecycle.
3. Document the Pages toolchain in README and site data, and add semantic drift checks so future docs changes do not silently downgrade the toolchain.
4. Verify current static build, docs build after upgrade, generated route/assets, `make clean test`, and `git diff --check`.
5. Push a focused PR branch.
