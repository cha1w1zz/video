import subprocess, sys
FF, CLIPDIR, SONG, LYR, OUT = sys.argv[1:6]
B = 0.4725                      # one beat (s)
SONG_START = 33.3               # "Take me down to the river"
# (clip, start, beats or seconds, speed). Cuts start ~0.15s before a detected gunshot.
pre = [(1,2.55,None,0.65,2.0)] + [(c,s,2,1,None) for c,s in
       [(3,2.45),(4,0.05),(2,3.8),(5,0.55),(3,4.1),(1,6.3),(4,2.8),(2,5.47),(3,6.6),(5,1.9),(1,7.13),(2,7.97),(3,7.97)]] \
      + [(4,8.55,2,0.5,None)]
post = [(c,s,b,1,None) for c,s,b in
       [(4,8.8,3),(3,9.63,2),(2,14.2,2),(5,6.43,1),(5,6.73,1),(3,16.95,2),(1,3.3,2),(4,12.53,2),
        (2,15.58,2),(1,8.07,2),(4,16.4,3),(5,8.28,2),(1,14.93,1),(1,15.63,1),(3,0.3,2)]] \
      + [(1,12.8,None,0.5,2.0)]
segs = []
for c,s,b,sp,dur in pre+post:
    out = dur if dur else b*B
    segs.append((c, s, out*sp, sp, out))
starts=[0]; 
for x in segs[:-1]: starts.append(starts[-1]+x[4])
total = starts[-1]+segs[-1][4]; DROP = starts[len(pre)]
def pulse(T,amp,k): return f"{amp}*exp(-(t-{T:.3f})*{k})*gte(t,{T:.3f})"
hits = [st+0.15 for st in starts[1:]]
Z = "(1+" + "+".join([pulse(DROP,0.45,5), pulse(DROP+7.55,0.35,5)] +
                     [pulse(h, 0.2 if h>DROP else 0.12, 10) for h in hits]) + ")"
shake = "+".join([f"30*sin(t*85)*exp(-(t-{T:.3f})*5)*gte(t,{T:.3f})" for T in (DROP, DROP+7.55)] +
                 [f"10*sin(t*70)*exp(-(t-{h:.3f})*12)*gte(t,{h:.3f})" for h in hits if h>DROP])
flash = "+".join([pulse(DROP,0.6,8), pulse(DROP+7.55,0.5,8)] +
                 [pulse(starts[i],0.28,12) for i in range(len(pre)+1,len(segs),2)])
args=[FF,"-v","error","-y"]
for c,s,src,sp,o in segs: args += ["-ss",f"{s}","-t",f"{src:.3f}","-i",f"{CLIPDIR}/c{c}.mp4"]
args += ["-i",SONG,"-i",LYR]
n=len(segs)
fc=";".join(f"[{i}:v]setpts=(PTS-STARTPTS)/{sp},fps=30,scale=1920:1080,setsar=1[s{i}]" for i,(_,_,_,sp,_) in enumerate(segs))
fc+=";"+"".join(f"[s{i}]" for i in range(n))+f"concat=n={n}:v=1:a=0,tmix=frames=2[c];"
fc+=(f"[c]scale=w='2*trunc(960*{Z})':h='2*trunc(540*{Z})':eval=frame,"
     f"crop=1920:1080:x='(iw-1920)/2+{shake}':y='(ih-1080)/2+0.5*({shake})',"
     "colorbalance=rs=-0.10:gs=0.04:bs=0.12:rm=-0.04:gm=0.02:bm=0.06:rh=0.05:bh=0.06,"
     f"eq=saturation=1.3:contrast=1.1:brightness='{flash}':eval=frame,split[g1][g2];"
     "[g2]gblur=sigma=18[gb];[g1][gb]blend=all_mode=screen:all_opacity=0.24,vignette=PI/5,format=yuv420p[bg];"
     f"[{n+1}:v]format=yuva420p[ly];[bg][ly]overlay=0:0:shortest=0:eof_action=pass,format=yuv420p[v];"
     f"[{n}:a]atrim={SONG_START}:{SONG_START+total:.3f},asetpts=PTS-STARTPTS,"
     f"afade=t=in:d=0.3,afade=t=out:st={total-1.2:.3f}:d=1.2[a]")
args+=["-filter_complex",fc,"-map","[v]","-map","[a]","-t",f"{total:.3f}","-c:v","libx264","-preset","medium",
       "-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",OUT]
subprocess.run(args,check=True)
print(f"done {total:.2f}s drop {DROP:.2f}s")
