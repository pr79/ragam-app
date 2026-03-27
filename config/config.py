"""Ragam App — Centralized Configuration
Version: 1.1.0 | Updated: 2026-03-26
Domain Agent: Music_Strategist_Agent reviewed
"""
import os
from dotenv import load_dotenv
load_dotenv()

# ── Audio Processing ──────────────────────────────────────────────────────────
DEMUCS_MODEL: str = os.getenv("RAGAM_DEMUCS_MODEL", "htdemucs_6s")
SUPPORTED_AUDIO_FORMATS: list[str] = ["mp3", "wav", "m4a", "flac", "ogg"]
ANALYSIS_DURATION_SEC: int = int(os.getenv("RAGAM_ANALYSIS_DURATION", "30"))

# ── Stem Separation ───────────────────────────────────────────────────────────
STEM_NAMES: list[str] = ["vocals", "bass", "drums", "piano", "guitar", "other"]
CUSTOM_STEMS: list[str] = ["flute", "percussion"]

# ── DSP Constants ─────────────────────────────────────────────────────────────
FLUTE_BANDPASS_LOW_HZ: int = int(os.getenv("RAGAM_FLUTE_LOW_HZ", "250"))
FLUTE_BANDPASS_HIGH_HZ: int = int(os.getenv("RAGAM_FLUTE_HIGH_HZ", "3500"))
HARMONIC_MARGIN: float = float(os.getenv("RAGAM_HARMONIC_MARGIN", "1.2"))
CLAHE_TILE_GRID: tuple[int, int] = (8, 8)
MORPHOLOGICAL_KERNEL: tuple[int, int] = (15, 15)

# ── Caching ──────────────────────────────────────────────────────────────────
CACHE_DIR: str = os.getenv("RAGAM_CACHE_DIR", "outputs/cache")
USE_CACHE: bool = os.getenv("RAGAM_USE_CACHE", "true").lower() == "true"

# ── Output ────────────────────────────────────────────────────────────────────
OUTPUT_DIR: str = os.getenv("RAGAM_OUTPUT_DIR", "outputs")
OUTPUT_DPI: int = int(os.getenv("RAGAM_OUTPUT_DPI", "300"))

# ── FFmpeg ────────────────────────────────────────────────────────────────────
FFMPEG_URL: str = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
FFMPEG_BIN_DIR: str = os.getenv("RAGAM_FFMPEG_DIR", "bin")

# ── Raga Analysis ─────────────────────────────────────────────────────────────
MIN_RAGA_CONFIDENCE: float = float(os.getenv("RAGAM_MIN_CONFIDENCE", "0.3"))

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR: str = os.getenv("LOG_DIR", "logs")
