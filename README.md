---
title: Ragam App
emoji: 🎵🚀
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: "1.40.0"
app_file: app.py
pinned: false
---

# Ragam App v1.1.0 — AI Music Separator & Raga Identifier

A Streamlit platform for AI-powered audio stem separation and Indian Classical Music (Raga) identification. Architecture reviewed by the **Music_Strategist_Agent** domain agent.

## What It Does

1. **6-Stem Source Separation** — Demucs `htdemucs_6s` splits audio into Vocals, Drums, Bass, Piano, Guitar, Other
2. **Custom DSP Instrument Extraction** — Harmonic/percussive isolation extracts Indian flute/wind and Indian percussion (Tabla/Mridangam) using bandpass filtering (250–3500 Hz)
3. **Karaoke & Custom Mixing** — Selectively mute/include stems, generate a custom mix WAV with download
4. **Raga Identification** — Chroma-based tonic detection matched against an Indian Classical Raga database, with Arohanam/Avarohanam display
5. **Dual Notation Transcription** — AI pitch extraction (Basic Pitch / Librosa fallback) with simultaneous Western (C, D#) and Carnatic Swara (Sa, Ga2) readout

## Setup

### Prerequisites

- Python 3.10 or 3.11
- FFmpeg (auto-downloaded by `setup_ffmpeg.py` on Windows; Homebrew on Mac)

### Install

```bash
git clone <repo-url>
cd ragam-app
pip install -r requirements.txt
python setup_ffmpeg.py   # downloads FFmpeg to bin/
```

### Configure (optional)

```bash
cp .env.example .env
# Edit .env to override defaults
```

### Run

```bash
streamlit run app.py
```

## Configuration

All constants are centralized in `config/config.py` and can be overridden via environment variables:

| Variable | Default | Description |
|---|---|---|
| `RAGAM_DEMUCS_MODEL` | `htdemucs_6s` | Demucs model (`htdemucs_6s` = 6-stem, `htdemucs` = 4-stem) |
| `RAGAM_ANALYSIS_DURATION` | `30` | Seconds of audio to analyze for raga/chord detection |
| `RAGAM_FLUTE_LOW_HZ` | `250` | Bandpass filter lower cutoff for flute DSP extraction (Hz) |
| `RAGAM_FLUTE_HIGH_HZ` | `3500` | Bandpass filter upper cutoff for flute DSP extraction (Hz) |
| `RAGAM_CACHE_DIR` | `outputs/cache` | Directory for Demucs MD5-cache (avoids re-separation) |
| `RAGAM_OUTPUT_DIR` | `outputs` | Root directory for stems and mixes |
| `RAGAM_OUTPUT_DPI` | `300` | DPI for any rendered output images |
| `RAGAM_FFMPEG_DIR` | `bin` | Local bin directory name containing ffmpeg executable |
| `RAGAM_MIN_CONFIDENCE` | `0.3` | Minimum confidence threshold for raga match acceptance |
| `RAGAM_HARMONIC_MARGIN` | `1.2` | HPSS harmonic margin for flute/wind extraction |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

## Tests

CI tests are intentionally lightweight — Demucs and PyTorch are NOT installed in CI (too large). Only config and pure-math functions are tested automatically.

```bash
# Run all tests (requires only: numpy scipy pytest python-dotenv)
pytest tests/ -v

# Config unit tests
pytest tests/test_config.py -v

# Integration / file-system tests
pytest tests/test_integration.py -v
```

### Test Coverage

**`tests/test_config.py`** — Unit tests:
- `DEMUCS_MODEL` is a non-empty string
- `SUPPORTED_AUDIO_FORMATS` has 3+ items, all lowercase, includes `mp3`
- `ANALYSIS_DURATION_SEC` positive
- `STEM_NAMES` has 4+ entries
- `FLUTE_BANDPASS_LOW_HZ < FLUTE_BANDPASS_HIGH_HZ`, both within 20–20000 Hz
- `HARMONIC_MARGIN >= 1.0`
- `MIN_RAGA_CONFIDENCE` in `(0.0, 1.0)`
- `OUTPUT_DPI > 0`
- Conditional: `detect_key_from_chroma` (skipped if music_theory not importable)

**`tests/test_integration.py`** — Config validation:
- `DEMUCS_MODEL` is a known Demucs variant
- Flute bandpass range covers practical flute range (low <= 500, high >= 2000)
- `SUPPORTED_AUDIO_FORMATS` contains `wav`
- `CACHE_DIR` and `FFMPEG_BIN_DIR` are non-empty strings

## CI/CD

GitHub Actions workflow at `.github/workflows/ci.yml` runs on push to `main`/`develop` and on pull requests to `main`. Installs only lightweight dependencies (numpy, scipy, pytest, python-dotenv) — Demucs/PyTorch are excluded from CI.

## Project Structure

```
ragam-app/
├── app.py                        # Streamlit UI and app coordinator
├── src/
│   ├── audio_processor.py        # Demucs, DSP, caching, mixing
│   ├── music_theory.py           # Key detection and Raga database
│   └── utils.py                  # File I/O and directory management
├── config/
│   └── config.py                 # Centralized constants (env-overridable)
├── tests/
│   ├── test_config.py            # Unit tests (config + music theory)
│   └── test_integration.py       # Integration tests
├── logs/                         # Log output directory
├── bin/                          # FFmpeg binaries (downloaded by setup_ffmpeg.py)
├── data/                         # Runtime data (uploads, outputs)
├── setup_ffmpeg.py               # FFmpeg bootstrap script
├── .env.example                  # Environment variable template
├── requirements.txt
├── ANALYTICS.md
├── TESTING_AND_LEARNINGS.md
└── .github/workflows/ci.yml
```

## Mac OS Support

```bash
bash mac_build.sh   # configures Homebrew, FFmpeg, Python venv
```

## Cloud Deployment (Hugging Face Spaces)

Deploy as a Streamlit Space. Add a `packages.txt` containing `ffmpeg` for the system dependency. See `MASTER_PROMPT.md` for full reproduction guide.

**Note:** Initial separation runs take 1–2 minutes depending on hardware; subsequent runs on the same file use MD5 caching for near-instant results.

---

Built with the Global Agent Framework SDLC.
