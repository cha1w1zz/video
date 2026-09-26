import subprocess, sys
FF, CLIPDIR, SONG, OUT = sys.argv[1:5]
# (clip, start, end, speed) — intro slow shots, then beat-cut highlights
segs = [(3,7.5,8.9,0.6),(1,2.6,3.5,0.6),
        (3,12.0,12.94,1),(1,7.0,7.94,1),(2,10.5,11.44,1),(2,11.8,12.74,1),(4,1.0,1.94,1),(4,3.0,3.94,1),
        (1,5.3,5.77,1),(1,6.2,6.67,1),(3,10.3,11.24,1),(4,15.0,15.94,1),(2,13.3,14.24,1),(1,11.6,12.54,1),
        (1,12.5,13.5,0.5),(2,15.0,15.94,1),(5,5.6,7.0,0.7)]
durs = [(b-a)/s for _,a,b,s in segs]
starts = [sum(durs[:i]) for i in range(len(segs))]
total = sum(durs); DROP = starts[2]; SONG_DROP = 48.55
def pulse(T,amp,k): return f"{amp}*exp(-(t-{T:.3f})*{k})*gte(t,{T:.3f})"
Z = "(1+" + "+".join([pulse(DROP,0.35,5)] + [pulse(t,0.1,9) for t in starts[3:]]) + ")"
shake = f"26*sin(t*85)*exp(-(t-{DROP:.3f})*6)*gte(t,{DROP:.3f})"
flash = "+".join([pulse(DROP,0.5,9)] + [pulse(starts[i],0.3,9) for i in (14,15)])
args = [FF,"-v","error","-y"]
for c,a,b,s in segs: args += ["-ss",str(a),"-t",str(b-a),"-i",f"{CLIPDIR}/c{c}.mp4"]
args += ["-i",SONG]
fc = ";".join(f"[{i}:v]setpts=(PTS-STARTPTS)/{s},fps=30,scale=1920:1080,setsar=1[s{i}]" for i,(_,_,_,s) in enumerate(segs))
fc += ";" + "".join(f"[s{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0[c];"
fc += (f"[c]scale=w='2*trunc(960*{Z})':h='2*trunc(540*{Z})':eval=frame,"
       f"crop=1920:1080:x='(iw-1920)/2+{shake}':y='(ih-1080)/2+0.5*{shake}',"
       "colorbalance=rs=-0.10:gs=0.04:bs=0.12:rm=-0.04:gm=0.02:bm=0.06:rh=0.05:gh=0.0:bh=0.06,"
       f"eq=saturation=1.25:contrast=1.08:brightness='{flash}':eval=frame,split[g1][g2];"
       "[g2]gblur=sigma=18[gb];[g1][gb]blend=all_mode=screen:all_opacity=0.22,vignette=PI/5[v];"
       f"[{len(segs)}:a]atrim={SONG_DROP-DROP:.3f}:{SONG_DROP-DROP+total:.3f},asetpts=PTS-STARTPTS,"
       f"afade=t=in:d=0.4,afade=t=out:st={total-1.0:.3f}:d=1.0[a]")
args += ["-filter_complex",fc,"-map","[v]","-map","[a]","-c:v","libx264","-preset","medium","-crf","19",
         "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",OUT]
subprocess.run(args,check=True)
print(f"done {total:.2f}s, drop at {DROP:.2f}s")
