import { chromium } from 'playwright-core';
import { fileURLToPath } from 'url';
import path from 'path';

const dir = path.dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox', '--force-color-profile=srgb'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto('file://' + path.join(dir, 'cards.html'));
await page.evaluate(() => document.fonts.ready);

const cards = ['s1','s2','s3','s4','s5','s6','s8'];
for (const id of cards) {
  await page.evaluate((id) => {
    document.querySelectorAll('.card').forEach(c => c.classList.remove('active'));
    document.getElementById(id).classList.add('active');
  }, id);
  await page.waitForTimeout(120);
  await page.screenshot({ path: path.join(dir, id + '.png'), omitBackground: id !== 's8' });
  console.log('shot', id);
}
await browser.close();
