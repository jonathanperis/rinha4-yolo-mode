---
layout: ../../layouts/BaseLayout.astro
title: Astro 6.4 platform lane | rinha4-yolo-mode docs
description: Astro 6.4 Markdown processor, Sätteri, and Cloudflare routing status for the rinha4-yolo-mode Pages site.
---

<article class="article-shell">
  <a class="back-link" href="/rinha4-yolo-mode/docs/">BACK TO DOCS</a>
  <p class="eyebrow">ASTRO 6.4 PLATFORM LANE</p>
  <h1>Astro 6.4 adoption</h1>

  This Pages surface now pins Astro 6.4 and exercises the new Markdown processor API with the Rust-backed Sätteri processor. The route you are reading is Markdown-rendered on purpose so the processor path stays covered by the production build.

  The deployment target remains static GitHub Pages. Cloudflare's new `cf()` advanced-routing helper is tracked as a future deployment lane, not active runtime code, because this repository does not run Astro SSR, Workers, or a custom `fetch()` handler.

  <section class="checklist" aria-label="Astro 6.4 checks">
    <h2>CHECKS AND SOURCE CUES</h2>
    <ul>
      <li>Astro dependency pinned to the 6.4 line.</li>
      <li><code>markdown.processor</code> is configured with <code>@astrojs/markdown-satteri</code>.</li>
      <li>This Markdown route verifies the processor during <code>bun run build</code>.</li>
      <li>Cloudflare <code>cf()</code> remains a migration gate only while output is <code>static</code> for GitHub Pages.</li>
    </ul>
  </section>
</article>
