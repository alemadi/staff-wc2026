import { chromium } from 'playwright-core';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

const dir = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30;
// beat id -> [duration seconds, opaque?]
const BEATS = {
  s1:[4.0,false], s2:[3.8,false], s3:[4.2,false], s4:[4.0,false],
  s5:[4.5,false], s6:[4.2,false], s8:[3.1,true],
};

const browser = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--no-sandbox','--force-color-profile=srgb'] });
const page = await browser.newPage({ viewport:{width:1080,height:1920}, deviceScaleFactor:1 });
await page.goto('file://'+path.join(dir,'cards.html'));
await page.evaluate(()=>document.fonts.ready);

for (const [beat,[D,opaque]] of Object.entries(BEATS)){
  const out = path.join(dir,'seq',beat);
  fs.rmSync(out,{recursive:true,force:true}); fs.mkdirSync(out,{recursive:true});
  const N = Math.round(D*FPS);
  for (let f=0; f<N; f++){
    const t = f/FPS;
    await page.evaluate(([b,tt,d])=>window.renderFrame(b,tt,d), [beat,t,D]);
    await page.screenshot({ path: path.join(out,'f'+String(f).padStart(4,'0')+'.png'), omitBackground: !opaque });
  }
  console.log('captured', beat, N, 'frames');
}
await browser.close();
