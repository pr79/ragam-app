"""Unit tests for Ragam App configuration and music theory utilities."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from config.config import (
    DEMUCS_MODEL, SUPPORTED_AUDIO_FORMATS, ANALYSIS_DURATION_SEC,
    STEM_NAMES, FLUTE_BANDPASS_LOW_HZ, FLUTE_BANDPASS_HIGH_HZ,
    HARMONIC_MARGIN, MIN_RAGA_CONFIDENCE, OUTPUT_DPI
)


# ── Config Tests ──────────────────────────────────────────────────────────────

def test_demucs_model_is_string():
    assert isinstance(DEMUCS_MODEL, str) and len(DEMUCS_MODEL) > 0

def test_supported_formats_non_empty():
    assert len(SUPPORTED_AUDIO_FORMATS) >= 3

def test_supported_formats_lowercase():
    assert all(f == f.lower() for f in SUPPORTED_AUDIO_FORMATS)

def test_mp3_in_supported_formats():
    assert "mp3" in SUPPORTED_AUDIO_FORMATS

def test_analysis_duration_positive():
    assert ANALYSIS_DURATION_SEC > 0

def test_stem_names_minimum():
    assert len(STEM_NAMES) >= 4

def test_flute_bandpass_low_less_than_high():
    assert FLUTE_BANDPASS_LOW_HZ < FLUTE_BANDPASS_HIGH_HZ

def test_flute_bandpass_audible_range():
    assert 20 <= FLUTE_BANDPASS_LOW_HZ
    assert FLUTE_BANDPASS_HIGH_HZ <= 20000

def test_harmonic_margin_above_one():
    assert HARMONIC_MARGIN >= 1.0

def test_min_raga_confidence_range():
    assert 0.0 < MIN_RAGA_CONFIDENCE < 1.0

def test_output_dpi_positive():
    assert OUTPUT_DPI > 0


# ── Music Theory Tests (conditional) ─────────────────────────────────────────

try:
    from src.music_theory import detect_key_from_chroma
    HAS_MUSIC_THEORY = True
except ImportError:
    HAS_MUSIC_THEORY = False

@pytest.mark.skipif(not HAS_MUSIC_THEORY, reason="music_theory not importable")
def test_detect_key_returns_string():
    import numpy as np
    # Mock chroma vector (12 pitches, uniform distribution)
    chroma = np.ones(12) / 12.0
    result = detect_key_from_chroma(chroma)
    assert isinstance(result, str)
