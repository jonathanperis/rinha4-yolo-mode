import { defineConfig } from 'astro/config';
import { satteri } from '@astrojs/markdown-satteri';

export default defineConfig({
  site: 'https://jonathanperis.github.io',
  base: '/rinha4-yolo-mode',
  output: 'static',
  markdown: {
    processor: satteri({
      features: { directive: true },
    }),
  },
});
