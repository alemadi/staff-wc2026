#!/usr/bin/env python3
"""Original cinematic score for the Staff Challenge 26 recap reel.
Scored to picture: section changes and impacts land on the edit's cut points.
Tonality: A minor / C major (relative-major lift on the trophy reveal).
"""
import numpy as np

SR = 44100
DUR = 25.4  # a touch longer than the 24.9s cut, for a reverb tail
N = int(SR * DUR)
t = np.arange(N) / SR

def env(a, d, s, r, sus_level, start, length):
    """ADSR envelope placed on the global timeline (seconds)."""
    e = np.zeros(N)
    i0 = int(start * SR); i1 = int((start + length) * SR)
    i1 = min(i1, N)
    seg = np.zeros(i1 - i0)
    n = len(seg)
    ai = int(a * SR); di = int(d * SR); ri = int(r * SR)
    idx = np.arange(n)
    # attack
    atk = np.clip(idx / max(ai, 1), 0, 1) * (idx < ai)
    # decay to sustain
    dec = (1 - (1 - sus_level) * np.clip((idx - ai) / max(di, 1), 0, 1)) * (idx >= ai)
    body = np.where(idx < ai, atk, dec)
    # release at tail
    rel_start = n - ri
    rel = np.clip((n - idx) / max(ri, 1), 0, 1)
    body = body * np.where(idx >= rel_start, rel, 1.0)
    seg = body
    e[i0:i1] = seg
    return e

def tone(freq, start, length, a, d, r, sus=0.8, detune=0.0, partials=(1.0,)):
    """Additive detuned sine voice with an ADSR."""
    sig = np.zeros(N)
    e = env(a, d, sus, r, sus, start, length)
    for p in partials:
        for dt in ([-detune, detune] if detune else [0.0]):
            f = freq * p * (2 ** (dt / 1200.0))
            phase = np.cumsum(np.full(N, 2 * np.pi * f / SR))
            sig += np.sin(phase)
    sig /= (len(partials) * (2 if detune else 1))
    return sig * e

def chord(freqs, start, length, a=1.2, d=1.5, r=1.6, sus=0.75, detune=7.0, gain=1.0):
    out = np.zeros(N)
    for f in freqs:
        out += tone(f, start, length, a, d, r, sus, detune, partials=(1.0, 2.0, 3.0))
    return out * gain / len(freqs)

# ---- notes ----
A1,A2,C3,E3,G3,C4,E4,G4,C5 = 55,110,130.81,164.81,196.0,261.63,329.63,392.0,523.25
F2,F3,A3,C2,G2,E2 = 87.31,174.61,220.0,65.41,98.0,82.41

mix = np.zeros(N)

# ---- SUB DRONE: follows the harmonic root through the sections ----
def sub(freq, start, length, gain=0.5):
    e = env(1.5, 1.0, 0.9, 1.5, 0.9, start, length)
    phase = np.cumsum(np.full(N, 2*np.pi*freq/SR))
    # sine + a little 2nd harmonic for body
    return (0.85*np.sin(phase) + 0.15*np.sin(2*phase)) * e * gain

mix += sub(A1, 0.0, 7.4)          # A minor
mix += sub(C2, 6.6, 4.6)          # C (trophy lift)
mix += sub(A1, 10.6, 4.2)         # A minor (tension)
mix += sub(F2, 14.2, 4.7)         # F (podium)
mix += sub(C2, 18.3, 7.1)         # C (champion + endcard resolve)

# ---- PADS per section (crossfading) ----
# A: Am  (0 - 7)
mix += chord([A2, C3, E3, A3], 0.0, 7.6, a=1.6, d=2.0, r=1.8, sus=0.7, gain=0.55)
# B: C major triumphant (7 - 10.8)
mix += chord([C3, E3, G3, C4, E4], 6.8, 4.4, a=0.9, d=1.6, r=1.4, sus=0.8, gain=0.72)
# C: Am sparse tension (10.8 - 14.4) — just root+fifth, quiet
mix += chord([A2, E3], 10.7, 3.9, a=0.7, d=1.4, r=1.2, sus=0.55, gain=0.4)
# D: F major rising (14.4 - 18.5)
mix += chord([F2, A3, C4, F3], 14.3, 4.5, a=1.1, d=1.8, r=1.5, sus=0.75, gain=0.6)
# E: C major warm resolve (18.5 - 22.3)
mix += chord([C3, E3, G3, C4], 18.4, 4.2, a=1.0, d=1.7, r=1.6, sus=0.8, gain=0.68)
# F: C major sustain into endcard tail (22.3 - end)
mix += chord([C3, G3, C4, E4], 22.2, 3.0, a=0.8, d=1.4, r=2.0, sus=0.75, gain=0.6)

# ---- RISER into the trophy reveal at 7.0 ----
def riser(peak, dur, gain=0.3):
    start = peak - dur
    i0, i1 = int(start*SR), int(peak*SR)
    seg = np.zeros(N)
    noise = np.random.normal(0, 1, N)
    # rising bandpass-ish: multiply noise by an upward-sweeping sine gate + envelope
    idx = np.arange(N)
    ramp = np.clip((idx - i0)/max(i1-i0,1), 0, 1)
    ramp = np.where((idx>=i0)&(idx<i1), ramp**2.2, 0.0)
    # tilt brighter as it rises
    sweep = np.sin(2*np.pi*(200 + 1400*ramp)*t)
    seg = noise*0.5*sweep*ramp + noise*ramp*0.15
    return seg*gain
mix += riser(7.05, 2.6, gain=0.22)

# ---- IMPACTS (cinematic booms) ----
def boom(at, gain=0.9, f=48, decay=1.1):
    i0 = int(at*SR)
    seg = np.zeros(N)
    n = N - i0
    idx = np.arange(n)
    tt = idx/SR
    # pitch drops from ~90 to f
    inst_f = f + 45*np.exp(-tt/0.12)
    phase = np.cumsum(2*np.pi*inst_f/SR)
    body = np.sin(phase)*np.exp(-tt/decay)
    # click transient
    click = (np.random.normal(0,1,n)*np.exp(-tt/0.02))*0.4
    seg[i0:] = (body + click)*gain
    return seg
mix += boom(7.0, gain=0.95)      # TROPHY / world champions — the hit
mix += boom(18.5, gain=0.6, decay=1.4)  # champion reveal — softer, warmer

# ---- TENSION PULSE (10.8 - 14.4), the "only 70 called it" section ----
def pulse(start, length, bpm=60, gain=0.35):
    seg = np.zeros(N)
    beat = 60.0/bpm
    at = start
    while at < start+length:
        i0 = int(at*SR)
        n = min(int(0.5*SR), N-i0)
        if n>0:
            idx=np.arange(n); tt=idx/SR
            f = 70 + 30*np.exp(-tt/0.05)
            ph = np.cumsum(2*np.pi*f/SR)
            seg[i0:i0+n]+= np.sin(ph)*np.exp(-tt/0.28)*gain
        at += beat
    return seg
mix += pulse(10.9, 3.4, bpm=66, gain=0.33)

# ---- SHIMMER bells at champion/maldives (18.5) ----
def bell(freq, at, gain=0.16, decay=2.2):
    i0=int(at*SR); n=N-i0; idx=np.arange(n); tt=idx/SR
    seg=np.zeros(N)
    tone_=(np.sin(2*np.pi*freq*tt)+0.5*np.sin(2*np.pi*2*freq*tt)+0.25*np.sin(2*np.pi*3.01*freq*tt))
    seg[i0:]= tone_*np.exp(-tt/decay)*gain
    return seg
for k,(f,off) in enumerate([(C5,0.0),(E4,0.18),(G4,0.42),(C5*1.5,0.9)]):
    mix += bell(f, 18.6+off, gain=0.13)
# a couple of high sparkles on the endcard
mix += bell(C5, 22.6, gain=0.10, decay=2.6)
mix += bell(G4, 23.1, gain=0.08, decay=2.6)

# ---- warm noise floor (very quiet tape hiss) ----
mix += np.random.normal(0,1,N)*0.006

# ================= simple stereo algorithmic reverb =================
def comb(x, delay_ms, fb, damp):
    d=int(delay_ms*SR/1000); y=np.copy(x); buf=0.0
    # vectorized-ish IIR via lfilter-like loop in chunks is slow; use scipy if available
    out=np.zeros(len(x)); store=np.zeros(d); last=0.0
    for i in range(len(x)):
        di=i%d
        delayed=store[di]
        last = delayed*(1-damp)+last*damp
        store[di]=x[i]+last*fb
        out[i]=delayed
    return out

# scipy makes reverb fast & clean
from scipy.signal import lfilter
def schroeder(x, wet=0.32):
    combs=[(29.7,0.805),(37.1,0.827),(41.1,0.783),(43.7,0.764)]
    acc=np.zeros(len(x))
    for ms,g in combs:
        d=int(ms*SR/1000)
        b=np.zeros(d+1); b[d]=1.0
        a=np.zeros(d+1); a[0]=1.0; a[d]=-g*0.9
        acc+=lfilter(b,a,x)
    acc/=len(combs)
    # allpass smear
    for ms,g in [(5.0,0.7),(1.7,0.7)]:
        d=int(ms*SR/1000)
        b=np.zeros(d+1); b[0]=-g; b[d]=1.0
        a=np.zeros(d+1); a[0]=1.0; a[d]=-g
        acc=lfilter(b,a,acc)
    return acc

wetL = schroeder(mix)
wetR = schroeder(np.concatenate([[0,0], mix[:-2]]))  # tiny offset for width
dry = mix
L = dry*0.72 + wetL*0.42
R = dry*0.72 + wetR*0.42

# ---- master: gentle global fade in/out, soft limiter ----
fade_in = np.clip(t/1.2, 0, 1)
tail_start = 24.6
fade_out = np.clip((DUR - t)/ (DUR-tail_start), 0, 1)
L*=fade_in*fade_out; R*=fade_in*fade_out

def limit(x, ceil=0.95):
    x = np.tanh(x*1.1)  # soft saturation glue
    peak=np.max(np.abs(x))
    if peak>0: x=x/peak*ceil
    return x
L=limit(L); R=limit(R)

stereo=np.stack([L,R],axis=1)
pcm=(stereo*32767).astype(np.int16)

import wave
with wave.open('/tmp/claude-0/-home-user-staff-wc2026/a9e2f00c-8728-536e-8266-1cd4cee1472a/scratchpad/reel/audio/score.wav','w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote score.wav", DUR, "s")
