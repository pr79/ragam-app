"""
Ragam App: Audio Processing Module
Handles source separation (Demucs), transcription (Basic Pitch/Librosa), and mixing.

Key Techniques:
1. Monkeypatching: We override demucs audio saving to use 'soundfile' for Windows stability.
2. MD5 Caching: Avoids duplicate processing of the same audio content.
3. Fallback Logic: Switches to Librosa if high-level AI models (Basic Pitch) are missing.
"""

import os
import subprocess
import hashlib
import shutil
import time
import sys
from pathlib import Path

import torch
import numpy as np
import soundfile as sf
import librosa

# Internal imports
from src.utils import OUTPUT_DIR

# --- FEATURE DETECTION: BASIC PITCH ---
# Spotify's Basic Pitch is preferred for transcription but requires TensorFlow/heavy setup.
try:
    from basic_pitch.inference import predict
    from basic_pitch import ICASSP_2022_MODEL_PATH
    BASIC_PITCH_AVAILABLE = True
except ImportError:
    BASIC_PITCH_AVAILABLE = False
    print("Basic Pitch not available. Transcription will use Librosa fallback.")

def get_file_hash(file_path):
    """
    Generates a unique MD5 hash for a file.
    Used for caching separation results to prevent redundant processing.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        # Read in 4KB chunks to be memory efficient
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def separate_audio(file_path, model_name="mdx_extra_q"):
    """
    Splits an audio file into 4 stems: Vocals, Drums, Bass, and Other.
    
    Args:
        file_path: Path to the input audio file.
        model_name: The Demucs model to use (default: mdx_extra_q for low RAM).
        
    Returns:
        Dictionary mapping stem names to their absolute file paths.
    """
    file_path = Path(file_path)
    file_hash = get_file_hash(file_path)
    
    # Define the unique directory for this specific file based on content hash
    clean_name = file_path.stem.replace(" ", "_")
    output_folder_name = f"{clean_name}_{file_hash[:8]}"
    track_dir = OUTPUT_DIR / model_name / output_folder_name
    
    expected_stems = {
        "vocals": track_dir / "vocals.wav",
        "drums": track_dir / "drums.wav",
        "bass": track_dir / "bass.wav",
        "other": track_dir / "other.wav"
    }
    
    # --- CACHE CHECK ---
    if all(p.exists() for p in expected_stems.values()):
        print(f"Demucs: Cache hit for {output_folder_name}")
        return expected_stems

    print(f"Demucs: Cache miss. Processing {file_path}...")

    # --- ENVIRONMENT VALIDATION ---
    # Ensure FFmpeg is accessible. It's often the culprit for 'NoBackendError'.
    ffmpeg_loc = shutil.which("ffmpeg")
    if not ffmpeg_loc:
        raise FileNotFoundError("FFmpeg not found. Ensure 'bin' folder exists and is in PATH.")

    # --- DYNAMIC MONKEYPATCHING ---
    # Torchaudio can be finicky on Windows. We force Demucs to use 'soundfile' for IO.
    import demucs.separate
    import demucs.audio
    
    def robust_save_audio(wav, path, sample_rate=None, **kwargs):
        sr = sample_rate if sample_rate is not None else kwargs.get("samplerate", 44100)
        # Convert torch tensor to numpy array
        if hasattr(wav, "detach"):
            data = wav.detach().cpu().numpy()
        else:
            data = wav
            
        # Reshape (Channels, Time) -> (Time, Channels) for soundfile compatibility
        if data.ndim == 2 and data.shape[0] < data.shape[1]:
             data = data.T
             
        sf.write(str(path), data, sr, subtype='PCM_16')
        
    # Apply patches
    demucs.audio.save_audio = robust_save_audio
    if hasattr(demucs.separate, "save_audio"):
        demucs.separate.save_audio = robust_save_audio
    
    # --- EXECUTION ---
    args = [
        "--out", str(OUTPUT_DIR),
        "-n", model_name,
        "--jobs", "1",
        str(file_path)
    ]
    
    try:
        demucs.separate.main(args)
        
        # Demucs creates a nested structure. We rename it to our hash-based folder.
        default_output_dir = OUTPUT_DIR / model_name / file_path.stem
        if default_output_dir.exists():
            if track_dir.exists():
                shutil.rmtree(track_dir)
            default_output_dir.rename(track_dir)
            
    except Exception as e:
        raise RuntimeError(f"Demucs separation failed: {e}")
        
    return expected_stems

def extract_pitch_librosa(file_path, duration=60):
    """
    Fallback transcription using Librosa's Probabilistic YIN (pYIN) algorithm.
    Optimized for short segments to avoid performance bottleneck.
    """
    try:
        # Load audio (mono, 22050Hz is usually sufficient for pitch)
        y, sr = librosa.load(str(file_path), sr=None, duration=duration)
        
        # Detect f0 (frequency) using pYIN
        # Ranges: C2 (~65Hz) to C7 (~2000Hz)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, 
            fmin=librosa.note_to_hz('C2'), 
            fmax=librosa.note_to_hz('C7')
        )
        
        times = librosa.frames_to_time(np.arange(len(f0)), sr=sr)
        note_events = []
        current_note = None
        start_time = 0
        
        # Aggregate consecutive frames of same pitch into 'note events'
        for i, (pitch, voiced) in enumerate(zip(f0, voiced_flag)):
            if not voiced or np.isnan(pitch):
                if current_note is not None:
                    note_events.append((start_time, times[i], current_note))
                    current_note = None
                continue
                
            midi_note = int(round(librosa.hz_to_midi(pitch)))
            
            if current_note is None:
                current_note = midi_note
                start_time = times[i]
            elif midi_note != current_note:
                note_events.append((start_time, times[i], current_note))
                current_note = midi_note
                start_time = times[i]
                
        # Handle trailing note
        if current_note is not None:
             note_events.append((start_time, times[-1], current_note))
             
        # Filter noise (notes shorter than 100ms)
        return str(file_path), [n for n in note_events if (n[1] - n[0]) > 0.1]
        
    except Exception as e:
        print(f"Librosa Transcription Error: {e}")
        return None, []

def transcribe_audio(file_path):
    """
    Attempts high-quality transcription with Basic Pitch, or falls back to Librosa.
    """
    if not BASIC_PITCH_AVAILABLE:
        return extract_pitch_librosa(file_path)

    try:
        # Basic Pitch prediction
        # Output: (model_output, note_data, note_events)
        _, midi_data, note_events = predict(
            str(file_path),
            ICASSP_2022_MODEL_PATH,
            onset_threshold=0.5,
            frame_threshold=0.3,
            minimum_note_length=58, # in ms
        )
        # Note: we don't save the MIDI to disk unless needed, we just pass the events
        return file_path, note_events
    except Exception as e:
        print(f"Basic Pitch Error: {e}. Falling back...")
        return extract_pitch_librosa(file_path)

def mix_stems(stem_paths, output_path):
    """
    Combines multiple stems into a single audio file with peak normalization.
    """
    master_audio = None
    common_sr = None
    
    for path in stem_paths:
        try:
            data, sr = sf.read(str(path))
            if master_audio is None:
                master_audio = data
                common_sr = sr
            else:
                # Synchronize lengths by trimming to the shortest track
                length = min(len(master_audio), len(data))
                master_audio = master_audio[:length] + data[:length]
        except Exception as e:
            print(f"Mixer: Skipped {path} due to error: {e}")
                
    if master_audio is not None:
        # Prevent clipping by normalizing to 0dB peak
        peak = np.max(np.abs(master_audio))
        if peak > 1.0:
            master_audio = master_audio / peak
            
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(out_file), master_audio, common_sr, subtype='PCM_16')
        return out_file
    
    return None
