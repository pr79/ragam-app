"""Integration tests — config and file system validation."""
import pytest
import os
from config.config import (
    DEMUCS_MODEL, SUPPORTED_AUDIO_FORMATS, FLUTE_BANDPASS_LOW_HZ,
    FLUTE_BANDPASS_HIGH_HZ, CACHE_DIR, OUTPUT_DIR, FFMPEG_BIN_DIR
)

def test_demucs_model_known_variant():
    known = ["htdemucs", "htdemucs_6s", "htdemucs_ft", "mdx", "mdx_extra"]
    assert DEMUCS_MODEL in known, f"Unknown model: {DEMUCS_MODEL}"

def test_flute_range_reasonable():
    # Human flute fundamental: ~262Hz-2093Hz; overtones extend to ~5kHz
    assert FLUTE_BANDPASS_LOW_HZ <= 500
    assert FLUTE_BANDPASS_HIGH_HZ >= 2000

def test_supported_formats_has_wav():
    assert "wav" in SUPPORTED_AUDIO_FORMATS

def test_cache_dir_string():
    assert isinstance(CACHE_DIR, str) and len(CACHE_DIR) > 0

def test_ffmpeg_bin_dir_string():
    assert isinstance(FFMPEG_BIN_DIR, str) and len(FFMPEG_BIN_DIR) > 0
