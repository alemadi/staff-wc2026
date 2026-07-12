// Leaderboard 🔥 streak chips office-wide (2026-07-12) — headless proof over the REAL page.
// Boots index.html against a mocked Supabase REST layer seeded with a QF-week world where
// four players sit at hand-built exact-score KO runs (me ×2 · a rival ×3 · a run-of-1 · a
// just-broken run), opens the People board and asserts the 🔥×N chip appears on EVERY row
// with a live run ≥2 — one's own row (locally computed, pre-analytics) AND other players'
// rows (CONS.koRun from the analytics tier) — and on nobody else. No live traffic, no writes.
// Run: node tests/lb-streak-chips/run.mjs  (env: CHROMIUM_BIN, PLAYWRIGHT_DIR, OUT_DIR)
import fs from 'fs';
import os from 'os';

const { chromium } = await import(process.env.PLAYWRIGHT_DIR || '/opt/node22/lib/node_modules/playwright/index.mjs');
const PAGE_URL = new URL('../../index.html', import.meta.url).href;
const SCRATCH = process.env.OUT_DIR || (os.tmpdir() + '/lb-streak-chips-out');
fs.mkdirSync(SCRATCH, { recursive: true });
const results = []; const fail = (m)=>{results.push(['FAIL',m]);console.log('FAIL',m);};
const pass = (m)=>{results.push(['PASS',m]);console.log('PASS',m);};
const FLAG_STUB_B64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGPYMj0SAAOnAaUfn5/rAAAAAElFTkSuQmCC';
const flagStub = (r)=>r.fulfill({status:200, contentType:'image/png', body:Buffer.from(FLAG_STUB_B64,'base64')});

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_BIN || '/opt/pw-browsers/chromium',
  args:['--force-prefers-reduced-motion'] });

/* ---------- PASS A: scrape fixture/bracket structure + scoring constants ---------- */
const ctxA = await browser.newContext();
const pgA = await ctxA.newPage();
await pgA.route('**://*.supabase.co/**', r=>r.fulfill({status:404, body:'{}'}));
await pgA.route('**://site.api.espn.com/**', r=>r.abort());
await pgA.route('**://fonts.googleapis.com/**', r=>r.fulfill({status:200, contentType:'text/css', body:''}));
await pgA.route('**://flagcdn.com/**', r=>r.abort());
await pgA.goto(PAGE_URL);
await pgA.waitForTimeout(800);
const world = await pgA.evaluate(()=>({
  fixtures: FIXTURES.map(f=>({id:f.id,ko:f.ko,kn:!!f.kn,round:f.round,tag:f.tag||null})),
  bracket: BRACKET, fl: FL, wnVer: (typeof WHATSNEW_VER!=='undefined')?WHATSNEW_VER:'',
  KO_PTS: (typeof KO_PTS!=='undefined')?KO_PTS:null, KO_BONUS: (typeof KO_BONUS!=='undefined')?KO_BONUS:null
}));
await ctxA.close();
console.log('scraped fixtures:', world.fixtures.length);
const KP = world.KO_PTS, KB = world.KO_BONUS;
const koPtsOf  = f => f.tag==='final'?KP.final:(f.tag==='third'?KP.third:(KP[f.round]||3));
const koBonusOf= f => f.tag==='final'?KB.final:(f.tag==='third'?KB.third:(KB[f.round]||0));

/* ---------- seeded world: all groups + R32 + R16 + first QF settled ---------- */
const fxById = {}; world.fixtures.forEach(f=>fxById[f.id]=f);
const qfs = world.fixtures.filter(f=>f.kn && f.round==='QF').sort((x,y)=>new Date(x.ko)-new Date(y.ko));
const qf0 = qfs[0];
const NOW = new Date(new Date(qfs[1].ko).getTime() + 40*60*1000).toISOString();

const teams = Object.keys(world.fl);
const pool = teams.slice(); let pi=0;
const kteams = {};
const r32ids = world.fixtures.filter(f=>f.kn&&f.round==='R32').map(f=>f.id);
r32ids.forEach(id=>{ kteams[id] = {h:pool[pi++],a:pool[pi++]}; });
const winner = id => kteams[id].h;               // home always advances
const results_ = {};
const groupFx = world.fixtures.filter(f=>!f.kn);
const SCORES = [{h:2,a:0},{h:1,a:0},{h:3,a:1},{h:1,a:1}];
groupFx.forEach((f,i)=>{ results_[f.id] = SCORES[i%4]; });
r32ids.forEach(id=>{ results_[id] = {w:winner(id), h:2, a:0}; });
const r16ids = world.fixtures.filter(f=>f.kn&&f.round==='R16').map(f=>f.id);
r16ids.forEach(id=>{ const [f1,f2]=world.bracket[id]; kteams[id]={h:winner(f1),a:winner(f2)}; results_[id]={w:kteams[id].h,h:2,a:0}; });
qfs.forEach(q=>{ const [f1,f2]=world.bracket[q.id]; kteams[q.id]={h:winner(f1),a:winner(f2)}; });
results_[qf0.id] = {w:kteams[qf0.id].h, h:2, a:1};

/* the exact-score walk orders engaged+settled KOs by NUMERIC id (koEngagedSettledKIds) */
const settledKo = [...r32ids, ...r16ids, qf0.id].sort((a,b)=>(+a.slice(1))-(+b.slice(1)));
console.log('settled KOs (walk order):', settledKo.join(','));

/* ---------- hand-built runs. Every player picks the correct WINNER on every settled KO
   (engaged everywhere), exactness controlled per position from the END of the walk:
   me ×2 live · aisha ×3 live · yousef run-of-1 (no chip) · omar just broken (no chip). ---------- */
function mkPlayer(slug, name, dept, exactFromEnd, missAt){
  // exactFromEnd: positions from the end (1 = last) that are EXACT; missAt: positions forced non-exact
  const predictions = {};
  settledKo.forEach((id,j)=>{
    const posFromEnd = settledKo.length - j;
    const r = results_[id];
    const pk = { w: r.w };
    if (exactFromEnd.includes(posFromEnd) && !missAt.includes(posFromEnd)) { pk.h = r.h; pk.a = r.a; }
    else { pk.h = r.h + 1; pk.a = r.a; }                  // engaged non-exact → resets the run
    predictions[id] = pk;
  });
  return { slug, name, dept, champ: null, predictions };
}
const blobs = [
  mkPlayer('khalid-almannai','Khalid Al-Mannai','Group Treasury',[1,2],[]),        // run ×2 (me)
  mkPlayer('aisha-alsulaiti','Aisha Al-Sulaiti','Compliance',[1,2,3],[]),          // run ×3
  mkPlayer('yousef-darwish','Yousef Darwish','Retail Banking',[1],[]),             // run 1 → no chip
  mkPlayer('omar-haddad','Omar Haddad','Group Risk',[2,3],[1]),                    // broken at the last KO → 0
  mkPlayer('sara-kamal','Sara Kamal','IT Operations',[],[]),                       // never exact
];
const EXPECT = { 'khalid-almannai':2, 'aisha-alsulaiti':3 };   // slug → chip ×N; everyone else: none

/* standings from the blobs (winner pts + exact bonus; streak/champ omitted — display only) */
function scoreOf(p){
  let pts=0,exact=0,correct=0,predicted=0;
  for(const id in p.predictions) predicted++;
  settledKo.forEach(id=>{ const f=fxById[id], r=results_[id], pk=p.predictions[id];
    if(pk.w===r.w){pts+=koPtsOf(f);correct++;}
    if(pk.h!=null&&+pk.h===r.h&&+pk.a===r.a){pts+=koBonusOf(f);exact++;}
  });
  return {pts,exact,correct,predicted};
}
const standings = blobs.map(p=>{ const s=scoreOf(p); return {slug:p.slug,name:p.name,dept:p.dept,pts:s.pts,exact:s.exact,correct:s.correct,predicted:s.predicted}; });

const KV = { 'wc:results': results_, 'wc:powerups_live': false };
blobs.forEach(b=>{ KV['wc:player:'+b.slug] = b; });

/* ---------- PASS B: boot signed in, open the People board ---------- */
const ctx = await browser.newContext({ viewport:{width:390,height:844} });
const pg = await ctx.newPage();
const errs = [];
pg.on('pageerror', e=>errs.push('PAGEERROR: '+e.message));
pg.on('console', m=>{ if(m.type()==='error' && !/Failed to load resource/.test(m.text())) errs.push('CONSOLE: '+m.text()); });

await pg.addInitScript(({now, meSlug, revealed, wnVer})=>{
  const off = new Date(now).getTime() - Date.now();
  const RD = Date;
  function ND(...a){ return a.length===0 ? new RD(RD.now()+off) : new RD(...a); }
  ND.now = ()=>RD.now()+off; ND.parse=RD.parse.bind(RD); ND.UTC=RD.UTC.bind(RD); ND.prototype=RD.prototype;
  window.Date = ND;
  localStorage.setItem('wc:me', JSON.stringify(meSlug));
  localStorage.setItem('wc:revealed', JSON.stringify(revealed));
  localStorage.setItem('wc:whatsnew', wnVer);
}, { now: NOW, meSlug: 'khalid-almannai', revealed: Object.keys(results_), wnVer: world.wnVer });

await pg.route('**://fonts.googleapis.com/**', r=>r.fulfill({status:200, contentType:'text/css', body:''}));
await pg.route('**://fonts.gstatic.com/**', r=>r.abort());
await pg.route('**://flagcdn.com/**', flagStub);
await pg.route('**://site.api.espn.com/**', r=>r.fulfill({status:200, contentType:'application/json', body:'{}'}));
await pg.route('**://*.supabase.co/**', r=>{
  const u = new URL(r.request().url());
  const send = (j)=>r.fulfill({status:200, contentType:'application/json', body:JSON.stringify(j)});
  if (u.pathname.endsWith('/rpc/server_time')) return send(NOW);
  if (u.pathname.endsWith('/rpc/standings')) return send(standings);
  if (u.pathname.endsWith('/rpc/consensus_counts')) return send({n:0,champN:0,champMap:{},map:{}});
  if (u.pathname.endsWith('/rpc/room_board')) return send([]);
  if (u.pathname.endsWith('/kv')) {
    const key = u.searchParams.get('key')||'';
    if (key.startsWith('in.')) {
      const names = decodeURIComponent(key.slice(3)).replace(/^\(|\)$/g,'').split(',').map(s=>s.replace(/^"|"$/g,'').replace(/\\"/g,'"'));
      return send(names.filter(k=>k in KV).map(k=>({key:k, value:JSON.stringify(KV[k])})));
    }
    if (key.startsWith('eq.')) { const k=decodeURIComponent(key.slice(3)); return send(k in KV ? [{key:k, value:JSON.stringify(KV[k])}] : []); }
    if (key.startsWith('like.')) { const pre=decodeURIComponent(key.slice(5)).replace(/\*$/,''); return send(Object.keys(KV).filter(k=>k.startsWith(pre)).sort().map(k=>({key:k, value:JSON.stringify(KV[k])}))); }
    return send([]);
  }
  return r.fulfill({status:404, body:'{}'});
});

await pg.goto(PAGE_URL);
await pg.waitForFunction(()=>typeof state!=='undefined' && state.player && state.meSlug==='khalid-almannai', null, {timeout:15000})
  .catch(()=>fail('boot: signed-in state not reached'));
await pg.waitForTimeout(600);
await pg.evaluate(()=>go('leaderboard'));

/* own-row chip: locally computed — must NOT wait for the analytics tier */
await pg.waitForSelector('.lb-row.me .lb-streak', {timeout:8000})
  .then(()=>pass('own-row 🔥 chip renders (local compute)')).catch(()=>fail('own-row chip missing'));

/* other rows enrich when consensusFull lands + silent re-render */
await pg.waitForSelector('.lb-row:not(.me) .lb-streak', {timeout:15000})
  .then(()=>pass('non-me 🔥 chip renders after the analytics tier')).catch(()=>fail('non-me chip never rendered'));
await pg.waitForTimeout(400);

const got = await pg.evaluate(()=>{
  const out = {rows:{}, koRun:(typeof CONS!=='undefined'&&CONS.koRun)||null};
  document.querySelectorAll('.lb-row').forEach(el=>{
    const nEl = el.querySelector('.lb-info .n'); if(!nEl) return;
    const name = nEl.childNodes[0] ? nEl.childNodes[0].textContent.trim() : nEl.textContent.trim();
    const chip = el.querySelector('.lb-streak');
    out.rows[name] = chip ? chip.textContent.trim() : null;
  });
  return out;
});
console.log('rows:', JSON.stringify(got.rows), '· CONS.koRun:', JSON.stringify(got.koRun));

const nameOf = s => blobs.find(b=>b.slug===s).name;
for (const slug in EXPECT) {
  const want = '🔥×'+EXPECT[slug], have = got.rows[nameOf(slug)];
  if (have===want) pass(nameOf(slug)+' shows '+want); else fail(nameOf(slug)+': expected '+want+' got '+have);
}
['yousef-darwish','omar-haddad','sara-kamal'].forEach(slug=>{
  const have = got.rows[nameOf(slug)];
  if (have==null) pass(nameOf(slug)+' has no chip (run < 2)'); else fail(nameOf(slug)+': unexpected chip '+have);
});
/* the map itself: >=2 only, nobody else leaks in */
const km = got.koRun||{};
if (km['aisha-alsulaiti']===3 && km['khalid-almannai']===2 && !('yousef-darwish' in km) && !('omar-haddad' in km) && !('sara-kamal' in km))
  pass('CONS.koRun holds exactly the ≥2 runs: '+JSON.stringify(km));
else fail('CONS.koRun wrong: '+JSON.stringify(km));

await pg.screenshot({ path: SCRATCH+'/lb-streak-chips-390.png', fullPage: true });
console.log('screenshot:', SCRATCH+'/lb-streak-chips-390.png');

if (errs.length) fail('page errors: '+errs.join(' | ')); else pass('zero page errors');
await browser.close();
const bad = results.filter(r=>r[0]==='FAIL').length;
console.log(bad ? ('\n'+bad+' FAILURE(S)') : '\nALL GREEN');
process.exit(bad ? 1 : 0);
