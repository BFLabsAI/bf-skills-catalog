#!/usr/bin/env node
/**
 * Export do Design System Ramon Pessoa / Inteligência Comercial.
 *
 * O ponto central: o viewport é ajustado para a dimensão exata do .canvas
 * antes do screenshot. Sem isso o navegador renderiza numa largura padrão e
 * a peça sai com sobra lateral.
 *
 *   node scripts/export.mjs                       → todos os templates
 *   node scripts/export.mjs ad-4x5-follow-up      → um template
 *   node scripts/export.mjs --pdf onepager-a4-*   → PDF (documentos)
 *   node scripts/export.mjs --scale 1             → 1x em vez de 2x
 */
import { chromium } from 'playwright';
import { readdirSync, mkdirSync, existsSync } from 'node:fs';
import { resolve, dirname, basename, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const TPL  = join(ROOT, 'templates');
const OUT  = join(ROOT, 'out');

const argv  = process.argv.slice(2);
const asPdf = argv.includes('--pdf');
const scale = Number(argv[argv.indexOf('--scale') + 1]) || (argv.includes('--scale') ? 2 : 2);
const names = argv.filter(a => !a.startsWith('--') && a !== String(scale));

const files = (names.length ? names.map(n => n.endsWith('.html') ? n : `${n}.html`)
                            : readdirSync(TPL).filter(f => f.endsWith('.html') && !f.startsWith('_')));

if (!existsSync(OUT)) mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
let done = 0, failed = 0;

for (const file of files) {
  const path = join(TPL, file);
  if (!existsSync(path)) { console.error(`✗ ${file} — não encontrado`); failed++; continue; }

  const page = await browser.newPage({ deviceScaleFactor: scale });
  await page.goto(pathToFileURL(path).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);

  // Dimensão real declarada pelo template — é ela que manda, não o viewport.
  const boxes = await page.$$eval('.canvas', els =>
    els.map(el => ({ w: Math.round(el.getBoundingClientRect().width),
                     h: Math.round(el.getBoundingClientRect().height) })));
  if (!boxes.length) { console.error(`✗ ${file} — sem .canvas`); failed++; await page.close(); continue; }

  const width  = Math.max(...boxes.map(b => b.w));
  const height = boxes.reduce((s, b) => s + b.h, 0);
  await page.setViewportSize({ width, height });
  await page.evaluate(() => document.fonts.ready);

  const stem = basename(file, '.html');
  if (asPdf) {
    await page.pdf({ path: join(OUT, `${stem}.pdf`), width: `${width}px`,
                     height: `${boxes[0].h}px`, printBackground: true, margin: {} });
    console.log(`✓ ${stem}.pdf   ${width}×${boxes[0].h} · ${boxes.length} página(s)`);
  } else if (boxes.length === 1) {
    await page.locator('.canvas').screenshot({ path: join(OUT, `${stem}.png`) });
    console.log(`✓ ${stem}.png   ${width}×${height} @${scale}x`);
  } else {
    const els = await page.locator('.canvas').all();
    for (const [i, el] of els.entries()) {
      await el.screenshot({ path: join(OUT, `${stem}-${i + 1}.png`) });
    }
    console.log(`✓ ${stem}-*.png  ${boxes.length} páginas @${scale}x`);
  }
  done++;
  await page.close();
}

await browser.close();
console.log(`\n${done} exportado(s)${failed ? ` · ${failed} com erro` : ''} → out/`);
process.exit(failed ? 1 : 0);
