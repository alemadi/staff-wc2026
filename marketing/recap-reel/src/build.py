#!/usr/bin/env python3
import subprocess, os, sys
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
ROOT = "/tmp/claude-0/-home-user-staff-wc2026/a9e2f00c-8728-536e-8266-1cd4cee1472a/scratchpad/reel"
CL, OV, OUT, AUD = f"{ROOT}/clips", f"{ROOT}/overlays", f"{ROOT}/out", f"{ROOT}/audio"
os.makedirs(OUT, exist_ok=True)
W, H, FPS, D = 1080, 1920, 30, 0.4  # xfade duration

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL:", " ".join(cmd[:6]), "...\n", r.stderr[-1500:]); sys.exit(1)

# segment: (clip file, overlay png, seg duration, trim in-point, speed factor)
SEG = [
    ("c1_tunnel.mp4",  "s1.png", 4.0, 0.0, 1.00),
    ("c2_cards.mp4",   "s2.png", 3.8, 0.0, 1.05),
    ("c3_trophy.mp4",  "s3.png", 4.2, 0.0, 1.12),  # hero beat, luxe slow-mo
    ("c4_lonecard.mp4","s4.png", 4.0, 0.0, 1.12),  # keep card from crowding text
    ("c5_podium.mp4",  "s5.png", 4.5, 0.0, 1.18),  # slow so leaderboard stays clear
    ("c6_maldives.mp4","s6.png", 4.2, 0.0, 1.08),  # champion, gentle slow-mo
]
ENDCARD = ("s8.png", 3.1)

def build_segment(i, clip, ov, dur, tin, speed):
    src = f"{CL}/{clip}"; ovp = f"{OV}/{ov}"; dst = f"{OUT}/seg{i}.mp4"
    fi_st, fi_d = 0.35, 0.55
    fo_st, fo_d = dur - 0.65, 0.55
    # base: trim, retime (speed), scale/crop to frame, set fps
    vf_base = (f"setpts=(PTS-STARTPTS)*{speed},"
               f"scale={W}:{H}:force_original_aspect_ratio=increase,"
               f"crop={W}:{H},fps={FPS},format=yuv420p")
    fc = (
        f"[0:v]trim=start={tin}:duration={dur/speed},{vf_base}[v];"
        f"[1:v]scale={W}:{H},format=rgba,"
        f"fade=in:st={fi_st}:d={fi_d}:alpha=1,fade=out:st={fo_st}:d={fo_d}:alpha=1[ov];"
        f"[v][ov]overlay=0:0:format=auto[o]"
    )
    run([FF, "-y", "-i", src, "-loop", "1", "-i", ovp,
         "-filter_complex", fc, "-map", "[o]", "-t", f"{dur}",
         "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", dst])
    return dst

def build_endcard(i, png, dur):
    dst = f"{OUT}/seg{i}.mp4"
    fc = (f"[0:v]scale={W}:{H},fps={FPS},"
          f"zoompan=z='min(zoom+0.0006,1.03)':d={int(dur*FPS)}:s={W}x{H}:fps={FPS},"
          f"format=yuv420p[o]")
    run([FF, "-y", "-loop", "1", "-i", f"{OV}/{png}", "-filter_complex", fc,
         "-map", "[o]", "-t", f"{dur}", "-c:v", "libx264", "-crf", "16",
         "-preset", "medium", "-pix_fmt", "yuv420p", dst])
    return dst

# ---- build all segments ----
segs, durs = [], []
for i,(clip,ov,dur,tin,sp) in enumerate(SEG, 1):
    if not os.path.exists(f"{CL}/{clip}"):
        print("MISSING", clip); sys.exit(2)
    segs.append(build_segment(i, clip, ov, dur, tin, sp)); durs.append(dur)
    print("built seg", i, clip)
segs.append(build_endcard(len(SEG)+1, *ENDCARD)); durs.append(ENDCARD[1])
print("built endcard")

# ---- xfade chain ----
inputs = []
for s in segs: inputs += ["-i", s]
fc = []
prev = "0:v"; off = 0.0
for i in range(1, len(segs)):
    off += durs[i-1] - D
    out = f"x{i}"
    fc.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={D}:offset={off:.3f}[{out}]")
    prev = out
chain = ";".join(fc)
total = sum(durs) - (len(segs)-1)*D
print("total video", round(total,2), "s")

# ---- global grade: bloom + warm grade + grain + vignette ----
grade = (
    f"[{prev}]split[g1][g2];"
    f"[g2]gblur=sigma=16[gb];"
    f"[g1][gb]blend=all_mode=screen:all_opacity=0.16[bloom];"
    f"[bloom]eq=contrast=1.07:saturation=1.09:gamma=0.98,"
    f"curves=r='0/0.015 0.5/0.54 1/1':g='0/0 0.5/0.5 1/0.99':b='0/0 0.5/0.46 1/0.95',"
    f"vignette=angle=PI/4.6,"
    f"noise=alls=5:allf=t+u,"
    f"format=yuv420p[graded]"
)
full = chain + ";" + grade
silent = f"{OUT}/video_silent.mp4"
run([FF, "-y", *inputs, "-filter_complex", full, "-map", "[graded]",
     "-c:v", "libx264", "-crf", "20", "-preset", "slow", "-pix_fmt", "yuv420p",
     "-maxrate", "16M", "-bufsize", "24M", "-r", str(FPS),
     "-movflags", "+faststart", silent])
print("wrote", silent)

# ---- mux score (trim/pad to video length, gentle fade tail) ----
final = f"{OUT}/StaffChallenge26_Recap.mp4"
run([FF, "-y", "-i", silent, "-i", f"{AUD}/score.wav",
     "-filter_complex", f"[1:a]afade=t=out:st={total-0.6:.2f}:d=0.6,atrim=0:{total:.2f}[a]",
     "-map", "0:v", "-map", "[a]",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", final])
print("FINAL", final)
