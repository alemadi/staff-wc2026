# Winner announcement reel — Higgsfield · LEGO theme · Instagram (9:16)

Production runbook for the Staff Challenge 26 champion-announcement reel.
Built to be executed on **Final night (19 July, ~21:00 Doha)** in under an hour:
generate the clips this week with placeholder-free scenes, then drop the real
names in as text overlays at the end — no AI regeneration needed on the night.

## The concept

A ~20-second brick-toy stop-motion reel: a miniature toy-brick World Cup
stadium at night, the podium built brick by brick, minifigures taking 3rd and
2nd, a drumroll, then the champion minifig hoisted up with the trophy under
gold confetti — ending on the Staff Challenge wordmark and the Maldives prize
reveal. Suspense order (3rd → 2nd → 1st) mirrors the app's podium.

Two rules that make or break it:

1. **Never ask the AI to render names, points, or logos.** Video models mangle
   text. Every clip is generated *textless*; names/points/prize go on as crisp
   text overlays in post (Instagram's own text tool, or CapCut). This is also
   what makes the reel buildable *before* the winner is known.
2. **Say "toy brick / minifigure style", not the brand name.** Some models
   silently degrade or refuse trademarked prompts; "brick-built toy world,
   glossy ABS plastic, stop-motion" gets the identical look reliably.

## Pipeline (Higgsfield)

1. **Keyframes first (Soul / image tab):** generate one 9:16 still per scene
   with the prompts below. Regenerate until the five stills feel like one set —
   reuse the best still as a *reference image* for the next scene to lock the
   look (same trick locks the minifig design across scenes).
2. **Animate (image-to-video):** feed each approved still + its motion prompt.
   3–5 s per clip, 9:16. Generate 2–3 takes per scene; keep the cleanest.
3. **Assemble:** stitch the five clips in order (CapCut / IG Reels editor),
   cut on the beat of a drumroll→cymbal track, add text overlays from the
   fill-in table, export 1080×1920.

Consistency beats cleverness: same "night stadium, warm gold floodlights"
lighting phrase in every prompt is what makes five separate generations read
as one film.

## Scene-by-scene prompts

House palette carried into every prompt: near-black background, warm gold
light, one red/green/blue accent (the app's tricolor bar).

### Scene 1 — The build-up (0–4 s)
- **Still:** Miniature toy-brick football stadium at night, built entirely of
  glossy plastic bricks, warm gold floodlights, dark navy sky with brick-stud
  stars, empty three-step podium at the center circle, red green and blue
  banner bricks on the stands, macro tilt-shift photography, stop-motion film
  still, 9:16 vertical.
- **Motion:** Slow cinematic push-in from above the stands toward the empty
  podium, floodlights flare gently, tiny brick confetti pieces drift; smooth
  dolly, no cuts.
- **Overlay (post):** `FULL TIME · THAT'S THE TOURNAMENT` → `STAFF CHALLENGE 26`

### Scene 2 — Third place (4–8 s)
- **Still:** Same brick stadium at night, a single smiling minifigure in
  office shirt stepping onto the lowest bronze podium step, bronze medal,
  spotlight from above, crowd of blurred minifigures cheering in the stands,
  stop-motion macro, 9:16.
- **Motion:** The minifigure hops onto the step and raises both arms, a
  bronze spotlight snaps on, subtle camera nudge closer; playful stop-motion
  cadence.
- **Overlay:** `🥉 3RD — {name} · {dept} · {pts} pts · 40,000 pts`

### Scene 3 — Second place (8–12 s)
- **Still:** Same set, a second minifigure leaping onto the middle silver
  podium step, silver medal, two spotlights now lit, more confetti bricks in
  the air, stands louder, stop-motion macro, 9:16.
- **Motion:** Minifig lands the jump and pumps a fist, silver spotlight snaps
  on, camera nudges closer again; slightly faster energy than scene 2.
- **Overlay:** `🥈 2ND — {name} · {dept} · {pts} pts · 60,000 pts`

### Scene 4 — The reveal (12–17 s) — the money shot
- **Still:** Same set, top podium step glowing gold but the champion hidden
  inside a brick-built golden trophy box, drumsticks on brick drums at the
  side, all floodlights converging, crowd frozen mid-cheer, 9:16.
- **Motion:** The trophy box bursts apart brick by brick revealing a champion
  minifigure holding the World Cup trophy overhead, gold confetti explosion,
  camera pops back then pushes in on the champion; triumphant slow-motion
  finish.
- **Overlay (timed to the burst):** `🥇 CHAMPION — {name}` → `{pts} pts` →
  `🏝 MALDIVES TRIP`

### Scene 5 — Outro (17–21 s)
- **Still:** Wide shot of the whole brick stadium erupting, fireworks built
  from translucent bricks over the roof, podium with all three minifigures,
  gold wash over everything, 9:16.
- **Motion:** Slow pull-back and tilt up to the fireworks, confetti settles,
  gentle fade toward dark.
- **Overlay:** `{champion team} — WORLD CHAMPIONS 2026` →
  `staffchallenge26.com` · `Staff World Cup 2026 · 11 June – 19 July`

## Fill-in on Final night (source: app leaderboard, once ftOver() is true)

| Slot | Where it goes | Value |
|---|---|---|
| `{name}` ×3, `{dept}` ×3, `{pts}` ×3 | Scenes 2–4 overlays | Final standings top 3 (board order = official tiebreaks) |
| `{champion team}` | Scene 5 overlay | Organizer champion set (`_champ`) |
| Optional honours line | Scene 5 | Oracle / Trailblazer / Hot Hand / Perfectionist from the Trophy Room |

Do not post before the organizer sets the champion in the app — that's the
moment standings are frozen and the +25 has paid. Same seal rule as every
share surface.

## Instagram post kit

- **Caption:** `FULL TIME. 38 days, 104 matches, one champion. 🥇 {name}
  takes the Maldives. 🥈 {name} · 🥉 {name} — thank you all for playing.
  Final standings → staffchallenge26.com`
- **Audio:** trending drumroll→celebration sound (pick on the night — reach);
  cut scene 4's burst on the cymbal hit.
- **Cover frame:** the scene-4 burst frame with `CHAMPION` overlay.
- **Backup plan:** if generation misbehaves on the night, the in-app
  **Podium share card** (`sharePodium()`) is the no-dependency fallback and
  posts as a static reel slide.

## Rehearsal checklist (this week)

- [ ] Generate the five stills; iterate until the set is consistent
- [ ] Animate all five; pick takes
- [ ] Assemble with placeholder text (`3RD — ???`) and check text safe-zones
      against IG Reels UI (keep overlays inside the center ~80%, nothing in
      the bottom ~320 px where the caption/actions sit)
- [ ] Time a full dry run: on the night only the text swap remains (~10 min)
