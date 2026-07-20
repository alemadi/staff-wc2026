# Staff Challenge 26 — "The Recap" (Instagram Reel)

A vertical (9:16) cinematic recap reel for the **Staff Challenge · World Cup 2026**
office prediction pool — cut as an epic film trailer.

**▶ Full-quality master (durable link):**
https://d2ol7oe51mr4n9.cloudfront.net/user_3GBHS1FBMMdIx9mNLLM7aQoNmtt/aeaec146-a456-4696-bd3c-5439bd97fb8e.mp4

| Spec | Value |
|------|-------|
| Resolution | 1080 × 1920 (9:16) |
| Frame rate | 30 fps |
| Duration | ~32.5 s |
| Video | H.264 High, yuv420p, Rec.709, faststart |
| Audio | AAC 48 kHz stereo |
| Loudness | −14 LUFS integrated, −1.0 dBTP (Instagram spec) |

## Concept

The reel is built as a trailer with a build-and-drop structure: the music (Heroic Age)
starts in its rising "breakdown" section under the opening beats, and the **champion
reveal lands exactly on the orchestral climax at t≈20.0 s**. A deep narrator carries a
sparse VO; narration deliberately drops out over the leaderboard beat so a riser + the
music surge take over into the reveal. Maldives is the bright emotional payoff before a
branded black end card.

## Edit / shot list

| # | Shot | In → Out | Beat |
|---|------|----------|------|
| 1 | Fireworks title — 104 MATCHES / 731 PLAYERS / ONE CHAMPION | 0.0–5.0 | "One office. One season. Everything on the line." |
| 2 | Office crowd — 23,755 CORRECT CALLS / 3,182 EXACT SCORELINES | 5.0–10.0 | "Twenty-three thousand correct calls. All of us — watching." |
| 3 | THE FINAL — SPAIN 1–0 ARGENTINA / ONLY 70 OF US CALLED IT | 10.0–15.0 | "It came down to one last match. Only seventy of us called it." |
| 4 | Leaderboard — DECIDED BY 4 POINTS (388 vs 384) | 15.0–20.0 | *(VO out — riser builds)* |
| — | dip to black | 19.82–20.0 | — |
| 5 | **CHAMPION — RUSHDY FOWZER · 388 PTS · 20 EXACT SCORES** | 20.0–25.2 | **DROP** + "Your champion… Rushdy Fowzer." |
| 6 | Maldives lagoon (the prize) | 25.2–29.6 | "The reward? Paradise itself. See you in 2030." |
| 7 | Branded end card (dissolve in) | 29.6–32.5 | — |

All numbers verified against the live site data (index.html / manifest.json).

## Voiceover

Generated with Higgsfield `seed_audio` TTS, preset voice **"Sterling"** (deep male).
Full script in [`vo-script.md`](./vo-script.md). Lines are trimmed, leveled to −16 LUFS,
placed on the timeline, and sidechain-duck the music bed for intelligibility.

## Sound design

Custom-synthesised in ffmpeg (no samples): a deep layered **boom** on the champion drop,
an airy **riser** into it, a **sub-drop** rolling under the reveal, and a **shimmer** into
the Maldives payoff. See [`scripts/generate_sfx.sh`](./scripts/generate_sfx.sh).

## Music — ATTRIBUTION REQUIRED

**"Heroic Age" by Kevin MacLeod (incompetech.com)** — licensed under
**Creative Commons: By Attribution 4.0** (https://creativecommons.org/licenses/by/4.0/).

Because this is CC-BY, the attribution **must** be credited when you post. Suggested caption line:

> Music: "Heroic Age" by Kevin MacLeod (incompetech.com) — CC BY 4.0

If you have an Artlist / Epidemic Sound / Musicbed subscription, swap in a fully-cleared
track and the reel can be re-cut to it (the whole build is scripted).

## Fonts

Anton, Bebas Neue, Oswald (Google Fonts, SIL Open Font License) — used only for the
end-card typography.

## Source assets

Designed story frames + B-roll were generated in Higgsfield (Kling 3.0 Turbo animations of
Nano Banana Pro poster frames; abstract B-roll via Kling 3.0 Turbo). See
[`assets.md`](./assets.md) for job IDs and CDN URLs.

## Rebuild

Scripts are in [`scripts/`](./scripts/). Run order (from a working dir holding the source
clips in `src/`, music/VO in `audio/`, fonts in `fonts/`):

```
scripts/build_segments.sh   # normalise 6 shots to 1080x1920/30
scripts/build_endcard.sh    # branded end card
scripts/generate_sfx.sh     # synthesised cinematic SFX
scripts/analyze.py          # music loudness-envelope analysis (climax finder)
scripts/build_video.sh      # concat + dissolve + cinematic grade
scripts/build_audio.sh      # music bed + VO + SFX + master to -14 LUFS
# final mux: see the ffmpeg mux command in this README's history / build notes
```

The `cd` lines in each script point at the build working directory; adjust to taste.
