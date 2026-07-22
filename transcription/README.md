# transcription

**Local transcription + speaker diarization on Apple Silicon: a video or
audio file in, a speaker-labelled transcript out. Free, private, and fast.**

Also published standalone at [github.com/haniabdemai/local-transcription](https://github.com/haniabdemai/local-transcription).

Local transcription guides usually hand you the slow CPU path
(whisper.cpp, faster-whisper via CTranslate2) and stop before the hard
part: knowing *who said what*. This pipeline runs ASR on the Apple GPU
via MLX (measured 18–28× realtime on M-series), runs pyannote speaker
diarization on the same GPU (MPS), and merges the two so every transcript
segment carries its speaker. Proven on a 22-hour real-world course corpus.
Nothing leaves your machine and nothing is billed.

Built on [mlx-whisper](https://github.com/ml-explore/mlx-examples)
(model `mlx-community/whisper-large-v3-turbo`) and
[pyannote.audio](https://github.com/pyannote/pyannote-audio)
(model `pyannote/speaker-diarization-community-1`). The models are their
work; this is the pipeline that makes them one tool.

## The scripts

| Script | Purpose |
|---|---|
| `mlx_transcribe.py` | ASR only: audio → JSON segments (mlx-whisper, Apple GPU) |
| `diarize.py` | Diarization only: audio → JSON speaker turns (pyannote on MPS, waveform pre-loaded for speed) |
| `process_lesson.py` | Full pipeline: transcribe → diarize → align speakers to segments → writes `<id>.segments.json` + a readable `<id>.txt` |

## Setup

Requires Apple Silicon, Python 3.11+, and ffmpeg on PATH.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export HF_TOKEN=your-hugging-face-token   # pyannote models are gated; accept
                                          # their terms on Hugging Face first
.venv/bin/python process_lesson.py path/to/recording.mp4
```

Usage: `process_lesson.py <input> [--out DIR] [--id ID] [--max-speakers N]`.
Any audio or video format ffmpeg can read is accepted; non-WAV input is
converted to 16 kHz mono WAV before processing. Outputs land in `./output/`
by default as `<id>.segments.json` and `<id>.txt`, where `<id>` defaults to
the input filename without its extension. Override with `--out` and `--id`.

The Hugging Face token is only needed for the diarization model download
(first run); `mlx_transcribe.py` alone needs no token.

## Adapting it

Speaker labels come out as `SPEAKER_00`, `SPEAKER_01` and so on. Rename
them in the emitted `.txt`/`.segments.json` once you know who is who, or
add your own label map to `process_lesson.py` for recurring speakers.

## Licence

MIT (this pipeline). The underlying models carry their own licences;
check mlx-whisper and pyannote before commercial use.
