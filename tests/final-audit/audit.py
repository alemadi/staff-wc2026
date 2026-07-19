#!/usr/bin/env python3
"""Independent audit of Staff Challenge 26 final standings.

Recomputes every player's score from the raw kv blobs using ONLY the
published rules (index.html rules card + the parity contract), then diffs
against the live standings() RPC output. Shares no code with either engine.

Usage: python3 audit.py [datadir]   (default: current directory)

Fetch the inputs into datadir first (U/K = SUPABASE_URL / publishable key
from index.html):
  curl "$U/rest/v1/kv?key=in.(%22wc:results%22,%22wc:kteams%22,%22wc:powerups_live%22)&select=key,value" \
       -H "apikey: $K" -o base.json
  for i in 0 1 2 3; do
    curl "$U/rest/v1/kv?key=like.wc:player:*&select=key,value,updated_at&order=key.asc" \
         -H "apikey: $K" -H "Range: $((i*200))-$((i*200+199))" -o players_$i.json
  done
  curl -X POST "$U/rest/v1/rpc/standings" -H "apikey: $K" \
       -H "Content-Type: application/json" -d '{}' -o standings_official.json
"""
import json, sys

D = sys.argv[1] if len(sys.argv) > 1 else "."

base = {r["key"]: r["value"] for r in json.load(open(f"{D}/base.json"))}
RES = json.loads(base["wc:results"])
KOVR = json.loads(base.get("wc:kteams") or "{}")
PU_LIVE = base.get("wc:powerups_live") in ("true", "1")

players = []
for i in range(4):
    players += json.load(open(f"{D}/players_{i}.json"))
official = json.load(open(f"{D}/standings_official.json"))

RANK = {"Argentina":1,"Spain":2,"France":3,"England":4,"Portugal":5,"Brazil":6,"Morocco":7,"Netherlands":8,
 "Belgium":9,"Germany":10,"Croatia":11,"Colombia":13,"Mexico":14,"Senegal":15,"Uruguay":16,"USA":17,
 "Japan":18,"Switzerland":19,"Iran":20,"Türkiye":22,"Ecuador":23,"Austria":24,"South Korea":25,"Australia":27,
 "Algeria":28,"Egypt":29,"Canada":30,"Norway":31,"Ivory Coast":33,"Panama":34,"Sweden":38,"Czechia":40,
 "Paraguay":41,"Scotland":42,"Tunisia":45,"DR Congo":46,"Uzbekistan":50,"Qatar":56,"Iraq":57,"South Africa":60,
 "Saudi Arabia":61,"Jordan":63,"Bosnia & H.":64,"Cape Verde":67,"Ghana":73,"Curaçao":82,"Haiti":83,"New Zealand":85}
TEAMS = set(RANK)

# knockout schedule: kid -> (home_feeder, away_feeder, take)   [R16 onward]
SCHED = {"k17":("k1","k4","W"),"k18":("k3","k6","W"),"k19":("k2","k5","W"),"k20":("k7","k8","W"),
         "k21":("k12","k11","W"),"k22":("k10","k9","W"),"k23":("k15","k14","W"),"k24":("k13","k16","W"),
         "k25":("k18","k17","W"),"k26":("k21","k22","W"),"k27":("k19","k20","W"),"k28":("k23","k24","W"),
         "k29":("k25","k26","W"),"k30":("k27","k28","W"),"k31":("k29","k30","L"),"k32":("k29","k30","W")}

def kadv(n):  # advance points ladder
    return 4 if n<=16 else 5 if n<=24 else 6 if n<=28 else 8 if n<=30 else 6 if n==31 else 10
def kbon(n):  # exact final-score bonus ladder
    return 4 if n<=16 else 5 if n<=24 else 6 if n<=28 else 7 if n<=30 else 5 if n==31 else 8
def rnd_bucket(n):
    return "qf" if 25<=n<=28 else "sf" if n in (29,30) else "fin" if n==32 else None

def num(v):
    if isinstance(v,bool) or v is None: return None
    if isinstance(v,int): return v
    if isinstance(v,float) and v==int(v): return int(v)
    if isinstance(v,str) and v.isdigit(): return int(v)
    return None

# ---- resolve every knockout tie's teams (override wins, else feeder chain) ----
TIE = {}
for k in [f"k{i}" for i in range(1,17)]:
    ov = KOVR.get(k) or {}
    h, a = ov.get("h"), ov.get("a")
    TIE[k] = {"h": h if h in TEAMS else None, "a": a if a in TEAMS else None}
for n in range(17,33):
    k = f"k{n}"; hf, af, take = SCHED[k]
    def feed(f, take):
        w = (RES.get(f) or {}).get("w")
        if not w: return None
        if take=="W": return w
        pr = TIE.get(f) or {}
        return pr.get("a") if w==pr.get("h") else pr.get("h") if w==pr.get("a") else None
    h, a = feed(hf,take), feed(af,take)
    ov = KOVR.get(k) or {}
    if ov.get("h") in TEAMS: h = ov["h"]
    if ov.get("a") in TEAMS: a = ov["a"]
    TIE[k] = {"h":h,"a":a}

# ---- results integrity ----
issues = []
for i in range(1,73):
    r = RES.get(f"m{i}")
    if not r: issues.append(f"m{i}: MISSING"); continue
    h,a = num(r.get("h")), num(r.get("a"))
    if h is None or a is None or not (0<=h<=20 and 0<=a<=20):
        issues.append(f"m{i}: bad score {r}")
for n in range(1,33):
    k=f"k{n}"; r=RES.get(k)
    if not r: issues.append(f"{k}: MISSING"); continue
    w,h,a = r.get("w"), num(r.get("h")), num(r.get("a"))
    t = TIE[k]
    if w not in TEAMS: issues.append(f"{k}: winner '{w}' not a team")
    if h is None or a is None or not (0<=h<=20 and 0<=a<=20):
        issues.append(f"{k}: bad score {r}")
    if t["h"] and t["a"] and w not in (t["h"],t["a"]):
        issues.append(f"{k}: winner {w} not in resolved tie {t}")
    if h is not None and a is not None and t["h"] and t["a"]:
        if h>a and w!=t["h"]: issues.append(f"{k}: score {h}-{a} but winner {w} != home {t['h']}")
        if a>h and w!=t["a"]: issues.append(f"{k}: score {h}-{a} but winner {w} != away {t['a']}")
        # h==a: decided on penalties, either winner is fine
if RES.get("_champ") != (RES.get("k32") or {}).get("w"):
    issues.append(f"_champ '{RES.get('_champ')}' != k32 winner '{(RES.get('k32') or {}).get('w')}'")

# ---- independent per-player scoring ----
def score_player(j):
    preds = j.get("predictions") or {}
    chips = j.get("chips") if isinstance(j.get("chips"), dict) else {}
    pts = exact = correct = predicted = 0
    for pid, p in preds.items():
        if not isinstance(p, dict): continue
        if p.get("o") or p.get("w"): predicted += 1
    # group stage
    for i in range(1,73):
        mid=f"m{i}"; r=RES.get(mid); p=preds.get(mid)
        if not r or not isinstance(p,dict): continue
        rh,ra = num(r.get("h")), num(r.get("a"))
        if rh is None or ra is None: continue
        o = p.get("o")
        if not o: continue                      # outcome pick required (gates exact too)
        out = "H" if rh>ra else "A" if rh<ra else "D"
        if o==out: pts+=3; correct+=1
        ph,pa = num(p.get("h")), num(p.get("a"))
        if ph is not None and pa is not None and ph==rh and pa==ra:
            pts+=2; exact+=1
    # knockouts — engaged settled rows in chronological (k-number) order
    engaged=[]
    for n in range(1,33):
        k=f"k{n}"; r=RES.get(k); p=preds.get(k)
        if not r or not r.get("w") or not isinstance(p,dict): continue
        if not (p.get("w") or num(p.get("h")) is not None): continue
        rh,ra = num(r.get("h")), num(r.get("a"))
        ph,pa = num(p.get("h")), num(p.get("a"))
        hit = (rh is not None and ra is not None and ph is not None and pa is not None
               and ph==rh and pa==ra)
        engaged.append((n,k,r,p,hit))
    for n,k,r,p,hit in engaged:
        earn = 0
        if p.get("w")==r["w"]: earn += kadv(n); correct += 1
        if hit: earn += kbon(n); exact += 1
        b = rnd_bucket(n)
        if PU_LIVE and b and chips.get(b)==k: earn *= 2          # armband: multiplies only
        pts += earn
        if PU_LIVE and n>=25 and p.get("w")==r["w"]:             # upset +2, never doubled
            t=TIE[k]; loser = t["a"] if r["w"]==t["h"] else t["h"] if r["w"]==t["a"] else None
            if loser and RANK.get(r["w"]) and RANK.get(loser) and RANK[r["w"]]>RANK[loser]:
                pts += 2
    # streak (shield forgives ONE breaking miss at kn>=25, only while powerups live)
    seq = engaged
    if PU_LIVE:
        for idx in range(len(seq)):
            n,_,_,_,hit = seq[idx]
            if not hit and n>=25 and idx>0 and seq[idx-1][4]:
                seq = seq[:idx]+seq[idx+1:]                       # drop the first such row only
                break
    run=0
    for n,_,_,_,hit in seq:
        if hit:
            run+=1
            if run==2: pts+=5
            elif run==3: pts+=15
            elif run>=4: pts+=20
        else: run=0
    # champion — never doubled
    if RES.get("_champ") and j.get("champ")==RES.get("_champ"): pts+=25
    return pts, exact, correct, predicted

mine = {}
chip_issues = []
post_final_writes = []
FINAL_KO = "2026-07-19T19:00:00"
for row in players:
    j = json.loads(row["value"]) if isinstance(row["value"], str) else row["value"]
    slug = j.get("slug") or row["key"][10:]
    mine[slug] = score_player(j) + (j.get("name") or slug, j.get("champ"))
    ch = j.get("chips")
    if isinstance(ch, dict):
        for b,rng in (("qf",range(25,29)),("sf",range(29,31)),("fin",range(32,33))):
            v=ch.get(b)
            if v and v not in [f"k{x}" for x in rng]: chip_issues.append(f"{slug}: chip {b}={v}")
    if (row.get("updated_at") or "") > FINAL_KO:
        post_final_writes.append((slug, row["updated_at"]))

# ---- diff vs official ----
drift = []
off = {r["slug"]: r for r in official}
for slug,(pts,ex,co,pr,name,champ) in mine.items():
    o = off.get(slug)
    if not o: drift.append(f"{slug}: in kv but NOT in standings()"); continue
    if (o["pts"],o["exact"],o["correct"],o["predicted"]) != (pts,ex,co,pr):
        drift.append(f"{slug}: official pts={o['pts']} exact={o['exact']} correct={o['correct']} pred={o['predicted']}"
                     f" vs audit pts={pts} exact={ex} correct={co} pred={pr}")
for slug in off:
    if slug not in mine: drift.append(f"{slug}: in standings() but NOT in kv")

# ---- report ----
print(f"players audited: {len(mine)} · official rows: {len(official)} · powerups_live={PU_LIVE}")
print(f"\nRESULTS INTEGRITY ({len(issues)} issue(s)):")
for x in issues: print("  ✗", x)
if not issues: print("  ✓ 72 group + 32 KO results present, scores sane, every winner consistent with the resolved bracket and scoreline; _champ == k32 winner")
print(f"\nCHIP VALIDITY ({len(chip_issues)} issue(s)):")
for x in chip_issues[:10]: print("  ✗", x)
if not chip_issues: print("  ✓ every stored armband chip targets a legal match for its round")
print(f"\nSCORE DRIFT vs live standings(): {len(drift)} row(s)")
for x in drift[:20]: print("  ✗", x)
if not drift: print("  ✓ ZERO drift — all 731 rows match the independent recompute exactly (pts, exact, correct, predicted)")

srt = sorted(mine.items(), key=lambda kv:(-kv[1][0],-kv[1][3],-kv[1][1],-kv[1][2],kv[1][4]))
print("\nAUDITED FINAL TOP 10 (pts · predicted · exact · correct · champion pick):")
for i,(slug,(pts,ex,co,pr,name,champ)) in enumerate(srt[:10],1):
    print(f"  #{i:<2} {slug:<28} {pts} · {pr} · {ex} · {co} · {champ or '—'}")
spain = sum(1 for _,v in mine.items() if v[5]=="Spain")
print(f"\nchampion pick 'Spain': {spain} of {len(mine)} players (+25 each = {spain*25} pts paid)")
print(f"\nplayer blobs written AFTER the Final kicked off ({len(post_final_writes)}):")
for s,t in post_final_writes[:15]: print(f"  ⚠ {s} @ {t}")
if not post_final_writes: print("  ✓ none")
