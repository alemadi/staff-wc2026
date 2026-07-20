#!/usr/bin/env python3
import subprocess, os, sys
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
ROOT = "/tmp/claude-0/-home-user-staff-wc2026/a9e2f00c-8728-536e-8266-1cd4cee1472a/scratchpad/reel"
CL, OV, OUT, AUD = f"{ROOT}/clips", f"{ROOT}/overlays", f"{ROOT}/out", f"{ROOT}/audio"
SEQ = f"{OV}/seq"
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL:", " ".join(str(c) for c in cmd[:8]), "...\n", r.stderr[-1800:]); sys.exit(1)

# --- hook (cold open): fast punch on the trophy, then white-flash into the tunnel ---
def build_hook():
    dst=f"{OUT}/seg0.mp4"; dur=0.7
    # take ~1.05s of source sped into 0.7s, with a slow scale push for energy
    vf=(f"trim=start=0:duration={dur*1.5:.3f},setpts=(PTS-STARTPTS)/1.5,"
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"zoompan=z='min(zoom+0.004,1.12)':d=1:s={W}x{H}:fps={FPS},"
        f"fps={FPS},format=yuv420p")
    run([FF,"-y","-i",f"{CL}/c3_trophy.mp4","-vf",vf,"-t",f"{dur}",
         "-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p",dst])
    return dst,dur

# text segment: clip (retimed) + animated overlay frame-sequence composited on top
def build_segment(i, clip, beat, dur, speed):
    src=f"{CL}/{clip}"; dst=f"{OUT}/seg{i}.mp4"
    vf_base=(f"setpts=(PTS-STARTPTS)*{speed},"
             f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
             f"fps={FPS},format=yuv420p")
    fc=(f"[0:v]trim=start=0:duration={dur/speed:.4f},{vf_base}[v];"
        f"[1:v]format=rgba[ov];[v][ov]overlay=0:0:format=auto[o]")
    run([FF,"-y","-i",src,"-framerate",str(FPS),"-i",f"{SEQ}/{beat}/f%04d.png",
         "-filter_complex",fc,"-map","[o]","-t",f"{dur}",
         "-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p",dst])
    return dst

# end card: animated opaque sequence is the base
def build_endcard(i, beat, dur):
    dst=f"{OUT}/seg{i}.mp4"
    run([FF,"-y","-framerate",str(FPS),"-i",f"{SEQ}/{beat}/f%04d.png",
         "-vf",f"scale={W}:{H},fps={FPS},format=yuv420p","-t",f"{dur}",
         "-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p",dst])
    return dst

# (clip, beat, dur, speed)
SEG=[
    ("c1_tunnel.mp4","s1",4.0,1.00),
    ("c2_cards.mp4","s2",3.8,1.05),
    ("c3_trophy.mp4","s3",4.2,1.12),
    ("c4_lonecard.mp4","s4",4.0,1.12),
    ("c5_podium.mp4","s5",4.5,1.18),
    ("c6_maldives.mp4","s6",4.2,1.08),
]
ENDCARD=("s8",3.1)

segs=[]; durs=[]; trans=[]
hook,hdur=build_hook(); segs.append(hook); durs.append(hdur); print("built hook")
trans.append(("fadewhite",0.20))   # hook -> tunnel : a flash
for i,(clip,beat,dur,sp) in enumerate(SEG,1):
    segs.append(build_segment(i,clip,beat,dur,sp)); durs.append(dur); print("built",beat)
    trans.append(("fade",0.40))
segs.append(build_endcard(len(SEG)+1,*ENDCARD)); durs.append(ENDCARD[1]); print("built endcard")
# trans has one entry per boundary between consecutive segs (len = nseg-1). We appended nseg entries; drop last.
trans=trans[:len(segs)-1]

# ---- xfade chain (per-boundary type/duration) ----
inputs=[];
for s in segs: inputs+=["-i",s]
fc=[]; prev="0:v"; off=0.0
for i in range(1,len(segs)):
    ttype,tdur=trans[i-1]
    off+=durs[i-1]-tdur
    out=f"x{i}"
    fc.append(f"[{prev}][{i}:v]xfade=transition={ttype}:duration={tdur}:offset={off:.3f}[{out}]")
    prev=out
chain=";".join(fc)
total=sum(durs)-sum(t[1] for t in trans)
print("total video", round(total,3),"s")

# ---- global grade: bloom + warm curves + grain + vignette ----
grade=(f"[{prev}]split[g1][g2];[g2]gblur=sigma=16[gb];"
       f"[g1][gb]blend=all_mode=screen:all_opacity=0.16[bloom];"
       f"[bloom]eq=contrast=1.07:saturation=1.09:gamma=0.98,"
       f"curves=r='0/0.015 0.5/0.54 1/1':g='0/0 0.5/0.5 1/0.99':b='0/0 0.5/0.46 1/0.95',"
       f"vignette=angle=PI/4.6,noise=alls=5:allf=t+u,format=yuv420p[graded]")
full=chain+";"+grade
silent=f"{OUT}/video_silent.mp4"
run([FF,"-y",*inputs,"-filter_complex",full,"-map","[graded]",
     "-c:v","libx264","-crf","20","-preset","slow","-pix_fmt","yuv420p",
     "-maxrate","16M","-bufsize","24M","-r",str(FPS),"-movflags","+faststart",silent])
print("wrote",silent)

# ---- mux score ----
final=f"{OUT}/StaffChallenge26_Recap.mp4"
run([FF,"-y","-i",silent,"-i",f"{AUD}/score.wav",
     "-filter_complex",f"[1:a]afade=t=out:st={total-0.6:.2f}:d=0.6,atrim=0:{total:.2f}[a]",
     "-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","256k","-shortest",final])
print("FINAL",final,"total",round(total,3))
