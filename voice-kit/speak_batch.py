"""Batch Thai voice cloning (F5-TTS-THAI). Loads the model once, speaks every
line of a script file, checks each line by transcribing it back, and retries
a line (different speed) if it came out wrong.

Usage:
  python speak_batch.py --ref ref.wav --ref-text "ข้อความที่พูดใน ref.wav" \
      --script lines.txt --outdir out [--steps 32] [--no-verify]
"""
import argparse, difflib, re, subprocess, time
from pathlib import Path
import soundfile as sf

p = argparse.ArgumentParser()
p.add_argument("--ref", required=True)
p.add_argument("--ref-text", default=None)
p.add_argument("--ref-text-file", default=None, help="text file from prep_ref.py")
p.add_argument("--allow-cpu", action="store_true", help="by default the script refuses to run without an NVIDIA GPU")
p.add_argument("--script", required=True, help="text file, one sentence per line")
p.add_argument("--outdir", default="out")
p.add_argument("--steps", type=int, default=32, help="16 = faster, 32 = better")
p.add_argument("--speeds", default="0.9,0.8,0.7,1.0", help="tried in order until a line verifies")
p.add_argument("--min-match", type=float, default=0.9)
p.add_argument("--no-verify", action="store_true")
p.add_argument("--no-polish", action="store_true", help="skip the gentle de-wind/de-hiss cleanup")
a = p.parse_args()
if a.ref_text_file: a.ref_text = Path(a.ref_text_file).read_text(encoding="utf-8").strip()
if not a.ref_text: p.error("give --ref-text or --ref-text-file")

import torch
from f5_tts_th.tts import TTS

device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device)
if device != "cuda" and not a.allow_cpu:
    raise SystemExit("No NVIDIA GPU (CUDA) found - stopping so it does not run slowly on CPU. Fix the torch CUDA install, or add --allow-cpu.")
tts = TTS(model="v1")

asr = None
if not a.no_verify:
    from faster_whisper import WhisperModel
    asr = WhisperModel("large-v3", device=device,
                       compute_type="float16" if device == "cuda" else "int8")

norm = lambda s: re.sub(r"[\s.,!?\"'“”‘’…\-]", "", s)
Path(a.outdir).mkdir(parents=True, exist_ok=True)
lines = [l.strip() for l in Path(a.script).read_text(encoding="utf-8").splitlines() if l.strip()]

for i, text in enumerate(lines, 1):
    best = None
    for sp in [float(x) for x in a.speeds.split(",")]:
        t = time.time()
        wav = tts.infer(ref_audio=a.ref, ref_text=a.ref_text, gen_text=text,
                        step=a.steps, cfg=2.0, speed=sp)
        out = Path(a.outdir) / f"{i:03d}.wav"
        sf.write(out, wav, 24000, subtype="FLOAT")  # float: the model output can exceed 1.0, int16 would clip (crackle)
        score = 1.0
        if asr:
            segs, _ = asr.transcribe(str(out), language="th", beam_size=5)
            heard = "".join(s.text for s in segs)
            score = difflib.SequenceMatcher(None, norm(text), norm(heard)).ratio()
        print(f"[{i}/{len(lines)}] speed={sp} match={score:.2f} {time.time()-t:.0f}s")
        if best is None or score > best[0]:
            best = (score, out.read_bytes())
        if score >= a.min_match:
            break
    Path(a.outdir, f"{i:03d}.wav").write_bytes(best[1])
    if best[0] < a.min_match:
        print(f"  !! line {i} still imperfect ({best[0]:.2f}) - listen to it / respell the words: {text}")
if not a.no_polish:
    # gentle tone fix (less boomy/muddy, a bit clearer): no gate/compressor, so it stays natural (not "studio")
    for f in sorted(Path(a.outdir).glob("[0-9][0-9][0-9].wav")):
        tmp = f.with_suffix(".tmp.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-af",
                        "volume=-6dB,highpass=f=90,equalizer=f=300:t=q:w=0.8:g=-2,lowpass=f=9000,loudnorm=I=-16:TP=-1.5",
                        "-ar", "24000", "-c:a", "pcm_s16le", str(tmp)], check=True)
        tmp.replace(f)
print("done ->", a.outdir)
