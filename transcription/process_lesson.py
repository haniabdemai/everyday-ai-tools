#!/usr/bin/env python
"""Full local transcription pipeline (Apple-Silicon GPU):
   mlx-whisper ASR  ->  pyannote diarization  ->  merge speakers  ->  readable transcript.

Usage: process_lesson.py <input> [--out DIR] [--id ID] [--max-speakers N]

Accepts any audio or video format ffmpeg can read; non-WAV input is
converted to 16 kHz mono WAV before processing.
Writes: <out>/<id>.segments.json  and  <out>/<id>.txt
"""
import argparse, json, os, subprocess, sys, tempfile, time, warnings
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(
    description="Local transcription + speaker diarization (Apple-Silicon GPU)."
)
parser.add_argument("input", help="audio or video file (any format ffmpeg can read)")
parser.add_argument("--out", default="./output",
                    help="output directory (default: ./output)")
parser.add_argument("--id", default=None,
                    help="output basename (default: derived from the input filename)")
parser.add_argument("--max-speakers", type=int, default=8,
                    help="maximum number of speakers for diarization (default: 8)")
args = parser.parse_args()

audio = args.input
out_dir = args.out
lid = args.id or os.path.splitext(os.path.basename(args.input))[0]
max_spk = args.max_speakers
os.makedirs(out_dir, exist_ok=True)

# ---------- 0. Convert non-WAV input to 16 kHz mono WAV (needed for diarization) ----------
tmp_wav = None
if not audio.lower().endswith(".wav"):
    fd, tmp_wav = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", audio, "-vn", "-ac", "1", "-ar", "16000", tmp_wav],
            check=True, capture_output=True)
    except FileNotFoundError:
        sys.exit("ffmpeg not found on PATH. Install it first (brew install ffmpeg).")
    except subprocess.CalledProcessError as e:
        os.unlink(tmp_wav)
        sys.exit(f"ffmpeg failed to convert {audio}:\n"
                 f"{e.stderr.decode(errors='replace')[-500:]}")
    audio = tmp_wav

try:
    # ---------- 1. ASR (GPU) ----------
    import mlx_whisper
    t0 = time.time()
    asr = mlx_whisper.transcribe(
        audio, path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
        language="en", word_timestamps=True, verbose=False, condition_on_previous_text=False)
    segs = [{"start": float(s["start"]), "end": float(s["end"]), "text": s["text"].strip()}
            for s in asr["segments"] if s["text"].strip()]
    t_asr = time.time() - t0
    dur = segs[-1]["end"] if segs else 0

    # ---------- 2. Diarization (GPU/MPS) ----------
    import torch, soundfile as sf
    from pyannote.audio import Pipeline
    t1 = time.time()
    pipe = Pipeline.from_pretrained("pyannote/speaker-diarization-community-1")
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    try: pipe.to(torch.device(dev))
    except Exception: dev = "cpu"; pipe.to(torch.device("cpu"))
    wav, sr = sf.read(audio, dtype="float32")
    wav = wav[None, :] if wav.ndim == 1 else wav.T
    inp = {"waveform": torch.from_numpy(wav), "sample_rate": sr}
    try:
        diar = pipe(inp, max_speakers=max_spk)
    except Exception:
        dev = "cpu"; pipe.to(torch.device("cpu")); diar = pipe(inp, max_speakers=max_spk)
    ann = getattr(diar, "exclusive_speaker_diarization", None) or getattr(diar, "speaker_diarization", diar)
    turns = [(float(t.start), float(t.end), spk) for t, _, spk in ann.itertracks(yield_label=True)]
    t_diar = time.time() - t1
finally:
    if tmp_wav and os.path.exists(tmp_wav):
        os.unlink(tmp_wav)

# ---------- 3. Merge: speaker = max temporal overlap ----------
def speaker_for(a, b):
    best, best_ov = None, 0.0
    for s, e, spk in turns:
        ov = max(0.0, min(b, e) - max(a, s))
        if ov > best_ov: best_ov, best = ov, spk
    return best or "SPEAKER_?"
for s in segs:
    s["speaker"] = speaker_for(s["start"], s["end"])

# ---------- 4. Write outputs ----------
json.dump({"id": lid, "duration_sec": dur, "segments": segs,
           "asr_seconds": t_asr, "diar_seconds": t_diar, "diar_device": dev},
          open(os.path.join(out_dir, f"{lid}.segments.json"), "w"), ensure_ascii=False, indent=1)

def hhmm(x):
    x = int(x); return f"{x//60:02d}:{x%60:02d}"
with open(os.path.join(out_dir, f"{lid}.txt"), "w") as f:
    cur = None
    for s in segs:
        if s["speaker"] != cur:
            cur = s["speaker"]; f.write(f"\n[{cur} @ {hhmm(s['start'])}]\n")
        f.write(s["text"] + " ")
speakers = sorted(set(s["speaker"] for s in segs))
print(f"{lid}: {dur/60:.0f}min audio | ASR {t_asr:.0f}s ({dur/max(t_asr,1):.1f}x) | "
      f"diar {t_diar:.0f}s ({dur/max(t_diar,1):.1f}x, {dev}) | speakers {speakers} | segs {len(segs)}")
