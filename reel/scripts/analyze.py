import subprocess, numpy as np

def load(path, sr=8000):
    p = subprocess.run(["ffmpeg","-v","error","-i",path,"-ac","1","-ar",str(sr),"-f","f32le","-"],
                       capture_output=True)
    return np.frombuffer(p.stdout, dtype=np.float32), sr

def envelope(path, name, bucket=4.0):
    x, sr = load(path)
    hop = int(0.5*sr)
    n = len(x)//hop
    rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop]**2)+1e-12) for i in range(n)])
    db = 20*np.log10(rms+1e-9)
    dbn = db - db.max()
    dur = len(x)/sr
    peak_t = int(np.argmax(rms))*0.5
    print(f"\n==== {name}   dur={dur:.0f}s   global peak @ {peak_t:.1f}s ====")
    per = int(bucket/0.5)
    for i in range(0, n, per):
        seg = dbn[i:i+per]
        t = i*0.5
        m = float(seg.mean())
        bar = "#"*max(0, int((m+36)/1.8))
        mark = "  <-- PEAK" if peak_t >= t and peak_t < t+bucket else ""
        print(f"{t:6.1f}s  {m:6.1f}dB  {bar}{mark}")

for path,name in [("audio/m_clash.mp3","CLASH DEFIANT"),
                  ("audio/m_heroic.mp3","HEROIC AGE"),
                  ("audio/m_raf.mp3","READY AIM FIRE")]:
    envelope(path, name)
