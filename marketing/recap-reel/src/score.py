#!/usr/bin/env python3
"""Original cinematic score, scored to the v2 cut (with cold-open hook).
Timeline (final): hook 0.0 | tunnel 0.5 | cards 4.1 | trophy 7.5 | lonecard 11.3
| podium 14.9 | maldives 19.0 | endcard 22.8 | end 25.9.
Tonality A minor / C major; relative-major lift on the trophy boom.
"""
import numpy as np, wave
from scipy.signal import lfilter

SR=44100; DUR=26.4; N=int(SR*DUR); t=np.arange(N)/SR

def env(a,d,sus,r,start,length):
    e=np.zeros(N); i0=int(start*SR); i1=min(int((start+length)*SR),N)
    n=i1-i0; idx=np.arange(n); ai=int(a*SR); di=int(d*SR); ri=int(r*SR)
    atk=np.clip(idx/max(ai,1),0,1)*(idx<ai)
    dec=(1-(1-sus)*np.clip((idx-ai)/max(di,1),0,1))*(idx>=ai)
    body=np.where(idx<ai,atk,dec)
    rel=np.clip((n-idx)/max(ri,1),0,1)
    body=body*np.where(idx>=n-ri,rel,1.0)
    e[i0:i1]=body; return e

def tone(freq,start,length,a,d,r,sus=0.8,detune=0.0,partials=(1.0,)):
    sig=np.zeros(N); e=env(a,d,sus,r,start,length)
    for p in partials:
        for dt in ([-detune,detune] if detune else [0.0]):
            f=freq*p*(2**(dt/1200.0))
            sig+=np.sin(np.cumsum(np.full(N,2*np.pi*f/SR)))
    sig/=(len(partials)*(2 if detune else 1)); return sig*e

def chord(freqs,start,length,a=1.2,d=1.5,r=1.6,sus=0.75,detune=7.0,gain=1.0):
    out=np.zeros(N)
    for f in freqs: out+=tone(f,start,length,a,d,r,sus,detune,partials=(1.0,2.0,3.0))
    return out*gain/len(freqs)

A1,A2,C3,E3,G3,C4,E4,G4,C5=55,110,130.81,164.81,196.0,261.63,329.63,392.0,523.25
F2,F3,A3,C2=87.31,174.61,220.0,65.41
mix=np.zeros(N)

def sub(freq,start,length,gain=0.5):
    e=env(1.5,1.0,0.9,1.5,start,length)
    ph=np.cumsum(np.full(N,2*np.pi*freq/SR))
    return (0.85*np.sin(ph)+0.15*np.sin(2*ph))*e*gain

mix+=sub(A1,0.4,7.1)      # Am  (tunnel+cards)
mix+=sub(C2,7.1,4.2)      # C   (trophy)
mix+=sub(A1,11.1,3.8)     # Am  (tension)
mix+=sub(F2,14.7,4.3)     # F   (podium)
mix+=sub(C2,18.8,7.1)     # C   (champion+endcard)

# pads
mix+=chord([A2,C3,E3,A3],0.4,7.3,a=1.6,d=2.0,r=1.8,sus=0.7,gain=0.55)   # Am
mix+=chord([C3,E3,G3,C4,E4],7.3,4.0,a=0.9,d=1.6,r=1.4,sus=0.8,gain=0.72) # C lift
mix+=chord([A2,E3],11.2,3.7,a=0.7,d=1.4,r=1.2,sus=0.55,gain=0.4)         # Am tension
mix+=chord([F2,A3,C4,F3],14.8,4.2,a=1.1,d=1.8,r=1.5,sus=0.75,gain=0.6)   # F
mix+=chord([C3,E3,G3,C4],18.9,3.9,a=1.0,d=1.7,r=1.6,sus=0.8,gain=0.68)   # C resolve
mix+=chord([C3,G3,C4,E4],22.7,3.2,a=0.8,d=1.4,r=2.0,sus=0.75,gain=0.6)   # C endcard

# riser into trophy reveal (7.5)
def riser(peak,dur,gain=0.3):
    start=peak-dur; i0,i1=int(start*SR),int(peak*SR)
    noise=np.random.normal(0,1,N); idx=np.arange(N)
    ramp=np.clip((idx-i0)/max(i1-i0,1),0,1); ramp=np.where((idx>=i0)&(idx<i1),ramp**2.2,0.0)
    sweep=np.sin(2*np.pi*(200+1400*ramp)*t)
    return (noise*0.5*sweep*ramp+noise*ramp*0.15)*gain
mix+=riser(7.55,2.6,gain=0.22)
mix+=riser(0.55,0.5,gain=0.14)   # tiny hook riser into the white flash

# impacts — now with a 150 Hz punch layer so they land on phone speakers
def boom(at,gain=0.9,f=48,decay=1.1,punch=0.6):
    i0=int(at*SR); n=N-i0; idx=np.arange(n); tt=idx/SR; seg=np.zeros(N)
    inst=f+45*np.exp(-tt/0.12); sub_=np.sin(np.cumsum(2*np.pi*inst/SR))*np.exp(-tt/decay)
    pun=np.sin(2*np.pi*150*tt)*np.exp(-tt/0.22)*punch          # mid punch (phone-audible)
    pun+=np.sin(2*np.pi*95*tt)*np.exp(-tt/0.30)*punch*0.6
    click=(np.random.normal(0,1,n)*np.exp(-tt/0.02))*0.4
    seg[i0:]=(sub_+pun+click)*gain; return seg
mix+=boom(7.50,gain=0.95)                 # trophy / world champions
mix+=boom(19.00,gain=0.6,decay=1.4)       # champion reveal
mix+=boom(0.55,gain=0.5,decay=0.7,punch=0.5)  # hook flash sting

# tension pulse (11.3-14.9)
def pulse(start,length,bpm=66,gain=0.33):
    seg=np.zeros(N); beat=60.0/bpm; at=start
    while at<start+length:
        i0=int(at*SR); n=min(int(0.5*SR),N-i0)
        if n>0:
            idx=np.arange(n); tt=idx/SR; f=70+30*np.exp(-tt/0.05)
            seg[i0:i0+n]+=np.sin(np.cumsum(2*np.pi*f/SR))*np.exp(-tt/0.28)*gain
        at+=beat
    return seg
mix+=pulse(11.4,3.4)

# shimmer bells at champion/endcard
def bell(freq,at,gain=0.13,decay=2.2):
    i0=int(at*SR); n=N-i0; idx=np.arange(n); tt=idx/SR; seg=np.zeros(N)
    tn=(np.sin(2*np.pi*freq*tt)+0.5*np.sin(2*np.pi*2*freq*tt)+0.25*np.sin(2*np.pi*3.01*freq*tt))
    seg[i0:]=tn*np.exp(-tt/decay)*gain; return seg
for f,off in [(C5,0.0),(E4,0.18),(G4,0.42),(C5*1.5,0.9)]: mix+=bell(f,19.05+off)
mix+=bell(C5,23.1,gain=0.10,decay=2.6); mix+=bell(G4,23.6,gain=0.08,decay=2.6)

mix+=np.random.normal(0,1,N)*0.006  # tape hiss

def schroeder(x):
    acc=np.zeros(len(x))
    for ms,g in [(29.7,0.805),(37.1,0.827),(41.1,0.783),(43.7,0.764)]:
        d=int(ms*SR/1000); b=np.zeros(d+1); b[d]=1.0; a=np.zeros(d+1); a[0]=1.0; a[d]=-g*0.9
        acc+=lfilter(b,a,x)
    acc/=4
    for ms,g in [(5.0,0.7),(1.7,0.7)]:
        d=int(ms*SR/1000); b=np.zeros(d+1); b[0]=-g; b[d]=1.0; a=np.zeros(d+1); a[0]=1.0; a[d]=-g
        acc=lfilter(b,a,acc)
    return acc

wetL=schroeder(mix); wetR=schroeder(np.concatenate([[0,0],mix[:-2]]))
L=mix*0.72+wetL*0.42; R=mix*0.72+wetR*0.42
fade_in=np.clip(t/0.8,0,1); tail=25.6; fade_out=np.clip((DUR-t)/(DUR-tail),0,1)
L*=fade_in*fade_out; R*=fade_in*fade_out
def limit(x,ceil=0.95):
    x=np.tanh(x*1.1); pk=np.max(np.abs(x));
    return x/pk*ceil if pk>0 else x
L=limit(L); R=limit(R)
pcm=(np.stack([L,R],axis=1)*32767).astype(np.int16)
with wave.open('/tmp/claude-0/-home-user-staff-wc2026/a9e2f00c-8728-536e-8266-1cd4cee1472a/scratchpad/reel/audio/score.wav','w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote score.wav", DUR,"s")
