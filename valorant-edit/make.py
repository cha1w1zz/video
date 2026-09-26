import subprocess, sys
FF, CLIP, SONG, OUT = sys.argv[1:5]
# (clip_start, clip_end, speed)
segs = [(0.0,3.0,1.5),(3.0,7.2,1.0),(7.2,7.7,0.4),(7.7,15.3,1.0),(6.2,8.4,0.5)]
DROP_OUT, SONG_DROP = 7.55, 48.55
total = sum((b-a)/s for a,b,s in segs)
replay_t = total - (8.4-6.2)/0.5
def pulse(T, amp, k): return f"{amp}*exp(-(t-{T})*{k})*gte(t,{T})"
punches = [pulse(DROP_OUT,0.4,5), pulse(2.0,0.12,8), pulse(6.2,0.18,6), pulse(replay_t,0.3,5)]
b = DROP_OUT + 0.94
while b < replay_t - 0.3:
    punches.append(pulse(round(b,2),0.1,9)); b += 0.94
Z = "(1+" + "+".join(punches) + ")"
shake = f"28*sin(t*85)*exp(-(t-{DROP_OUT})*6)*gte(t,{DROP_OUT})"
flash = "+".join(pulse(T,a,10) for T,a in [(DROP_OUT,0.55),(replay_t,0.4),(2.0,0.25),(6.2,0.25)])
parts, labels = [], ""
for i,(a,bb,s) in enumerate(segs):
    parts.append(f"[0:v]trim={a}:{bb},setpts=(PTS-STARTPTS)/{s},fps=30[s{i}]"); labels += f"[s{i}]"
fc = ";".join(parts) + f";{labels}concat=n={len(segs)}:v=1:a=0[c];" \
     f"[c]scale=w='2*trunc(960*{Z})':h='2*trunc(540*{Z})':eval=frame," \
     f"crop=608:1080:x='(iw-608)/2+{shake}':y='(ih-1080)/2+0.5*{shake}'," \
     f"scale=1080:1920,eq=saturation=1.35:contrast=1.12:brightness='{flash}':eval=frame[v];" \
     f"[1:a]atrim={SONG_DROP-DROP_OUT}:{SONG_DROP-DROP_OUT+total},asetpts=PTS-STARTPTS,afade=t=out:st={total-0.8}:d=0.8[a]"
subprocess.run([FF,"-v","error","-y","-i",CLIP,"-i",SONG,"-filter_complex",fc,"-map","[v]","-map","[a]",
  "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",OUT],check=True)
print(f"done {total:.2f}s")
