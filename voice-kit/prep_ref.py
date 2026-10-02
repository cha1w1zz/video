"""Make the reference voice (ref.wav + ref.txt) from your own recording.
Runs on the NVIDIA GPU. Picks the clearest continuous 5-8 s stretch of speech,
removes boominess with EQ (no AI denoiser), and writes the transcript.

  python prep_ref.py Cleanmark.m4a            -> ref.wav, ref.txt
CHECK ref.txt against what you really said and fix wrong words
(English words -> Thai reading, e.g. เทรน).
"""
import os, torch
os.environ["PATH"] = os.path.join(os.path.dirname(torch.__file__), "lib") + os.pathsep + os.environ["PATH"]
import subprocess, sys
from pathlib import Path

EQ = ("highpass=f=100,equalizer=f=300:t=q:w=0.8:g=-4,equalizer=f=650:t=q:w=1:g=-3,"
      "equalizer=f=4000:t=q:w=0.7:g=4,loudnorm=I=-18:TP=-2")

def best_window(words, lo=5.0, hi=8.0, max_gap=0.35):
    """words: [(text,start,end)]. Longest run of words with no pause > max_gap, lo..hi seconds."""
    best = None
    for i in range(len(words)):
        j = i
        while j + 1 < len(words) and words[j+1][1] - words[j][2] <= max_gap and words[j+1][2] - words[i][1] <= hi:
            j += 1
        dur = words[j][2] - words[i][1]
        if dur >= lo and (best is None or dur > best[2]):
            best = (i, j, dur)
    return best

if __name__ == "__main__":
    src = sys.argv[1]
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",src,"-ac","1","-ar","24000","_full.wav"], check=True)
    import torch
    from faster_whisper import WhisperModel
    dev = "cuda" if torch.cuda.is_available() else None
    if dev is None: raise SystemExit("No NVIDIA GPU (CUDA) found - stopping (GPU only).")
    m = WhisperModel("large-v3", device="cuda", compute_type="float16")
    segs, _ = m.transcribe("_full.wav", language="th", beam_size=5, word_timestamps=True)
    words = [(w.word, w.start, w.end) for s in segs for w in s.words]
    b = best_window(words)
    if not b: raise SystemExit("No clear 5-8 s stretch of speech found - record a longer, steadier clip.")
    i, j, dur = b
    t0, t1 = words[i][1], words[j][2]
    text = "".join(w[0] for w in words[i:j+1]).strip()
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i","_full.wav","-ss",f"{t0:.2f}","-to",f"{t1:.2f}",
                    "-af",EQ,"-ar","24000","-ac","1","ref.wav"], check=True)
    Path("ref.txt").write_text(text, encoding="utf-8")
    print(f"ref.wav {t0:.1f}-{t1:.1f}s ({dur:.1f}s)\nref.txt: {text}\n-> CHECK ref.txt and fix wrong words!")
