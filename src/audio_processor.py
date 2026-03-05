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
import socket
import urllib.error
import scipy.signal

# --- IMAGEIO FFMPEG INJECTION ---
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    os.environ['PATH'] += os.pathsep + os.path.dirname(ffmpeg_exe)
except ImportError:
    pass


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

def extract_flute_and_wind(other_path, out_path):
    if Path(out_path).exists(): return out_path
    try:
        y, sr = librosa.load(other_path, sr=None)
        # Harmonic extraction
        y_harm, y_perc = librosa.effects.hpss(y, margin=1.2)
        # Bandpass filter (250Hz - 3500Hz)
        sos = scipy.signal.butter(10, [250, 3500], 'bandpass', fs=sr, output='sos')
        y_flute = scipy.signal.sosfilt(sos, y_harm)
        sf.write(out_path, y_flute, sr, subtype='PCM_16')
    except Exception as e:
        print(f"Flute DSP error: {e}")
        shutil.copy2(other_path, out_path)
    return out_path

def extract_indian_percussion(other_path, drums_path, out_path):
    if Path(out_path).exists(): return out_path
    try:
        y_other, sr = librosa.load(other_path, sr=None)
        y_drums, _ = librosa.load(drums_path, sr=sr)
        # Ensure same length
        length = min(len(y_other), len(y_drums))
        y_other = y_other[:length]
        y_drums = y_drums[:length]
        
        # Extract percussion from both
        _, y_perc_other = librosa.effects.hpss(y_other, margin=2.0)
        _, y_perc_drums = librosa.effects.hpss(y_drums, margin=2.0)
        
        # Mix percussions
        y_indian_perc = (y_perc_other + y_perc_drums) / 2.0
        sf.write(out_path, y_indian_perc, sr, subtype='PCM_16')
    except Exception as e:
        print(f"Percussion DSP error: {e}")
        shutil.copy2(drums_path, out_path)
    return out_path

def extract_acoustic_guitar(guitar_path, out_acoustic):
    if Path(out_acoustic).exists():
        return out_acoustic
    try:
        y, sr = librosa.load(guitar_path, sr=None, mono=False)
        if y.ndim == 1 or y.shape[0] == 1:
            sf.write(out_acoustic, y.T if y.ndim > 1 else y, sr, subtype='PCM_16')
        else:
            left, right = y[0], y[1]
            side = (left - right) / 2.0
            sf.write(out_acoustic, side, sr, subtype='PCM_16')
    except Exception as e:
        print(f"Acoustic Guitar DSP error: {e}")
        shutil.copy2(guitar_path, out_acoustic)
    return out_acoustic


def separate_audio(file_path, model_name="htdemucs_6s"):
    """
    Splits an audio file into 6 base stems: Vocals, Drums, Bass, Piano, Guitar, Other.
    Then applies DSP to extract: Flute/Wind, Indian Percussion, Acoustic Guitar.
    
    Args:
        file_path: Path to the input audio file.
        model_name: The Demucs model to use (default: htdemucs_6s).
        
    Returns:
        Dictionary mapping stem names to their absolute file paths.
    """
    file_path = Path(file_path)
    file_hash = get_file_hash(file_path)
    
    # Define the unique directory for this specific file based on content hash
    clean_name = file_path.stem.replace(" ", "_")
    output_folder_name = f"{clean_name}_{file_hash[:8]}"
    track_dir = OUTPUT_DIR / model_name / output_folder_name
    
    # Base demucs stems
    demucs_stems = {
        "vocals": track_dir / "vocals.wav",
        "drums": track_dir / "drums.wav",
        "bass": track_dir / "bass.wav",
        "piano": track_dir / "piano.wav",
        "guitar": track_dir / "guitar.wav",
        "other": track_dir / "other.wav"
    }
    
    # Derived stems
    derived_stems = {
        "flute_and_wind": track_dir / "flute_and_wind.wav",
        "indian_percussion": track_dir / "indian_percussion.wav",
        "acoustic_guitar": track_dir / "acoustic_guitar.wav"
    }
    
    expected_stems = {**demucs_stems, **derived_stems}
    
    # --- CACHE CHECK ---
    if all(p.exists() for p in expected_stems.values()):
        print(f"Demucs & DSP: Cache hit for {output_folder_name}")
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
        str(file_path)
    ]
    
    try:
        import socket
        # Set a default timeout for underlying socket operations (e.g. model downloads)
        socket.setdefaulttimeout(15.0)
        
        # Only run demucs if base stems are missing
        if not all(p.exists() for p in demucs_stems.values()):
            demucs.separate.main(args)
            
            # Demucs creates a nested structure. We rename it to our hash-based folder.
            default_output_dir = OUTPUT_DIR / model_name / file_path.stem
            if default_output_dir.exists():
                if track_dir.exists():
                    shutil.rmtree(track_dir)
                default_output_dir.rename(track_dir)
                
        # --- POST-PROCESSING DSP ---
        # The guitar and other stems might be missing if Demucs failed or the model wasn't 6s
        if (track_dir / "other.wav").exists():
            extract_flute_and_wind(track_dir / "other.wav", track_dir / "flute_and_wind.wav")
            if (track_dir / "drums.wav").exists():
                extract_indian_percussion(track_dir / "other.wav", track_dir / "drums.wav", track_dir / "indian_percussion.wav")
        else:
             # Fallbacks if other is missing
             (track_dir / "flute_and_wind.wav").touch()
             (track_dir / "indian_percussion.wav").touch()

        if (track_dir / "guitar.wav").exists():
            extract_acoustic_guitar(track_dir / "guitar.wav", track_dir / "acoustic_guitar.wav")
        else:
             (track_dir / "acoustic_guitar.wav").touch()
            
    except socket.timeout:
        raise RuntimeError(f"Connection timed out after 15s. The distant server or proxy failed to respond.")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network routing failed. The server cannot be reached: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Demucs separation / DSP failed: {e}")
        
    return {k: v for k, v in expected_stems.items() if v.exists() and v.stat().st_size > 0}

def extract_pitch_librosa(file_path, duration=60):
    """
    Fallback transcription using Librosa's Probabilistic YIN (pYIN) algorithm.
    Optimized for short segments to avoid performance bottleneck.
    """
    try:
        import socket
        socket.setdefaulttimeout(15.0)

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
             
        # Filter noise: increase threshold to 150ms instead of 100ms
        return str(file_path), [n for n in note_events if (n[1] - n[0]) > 0.15]
        
    except socket.timeout:
        print("Librosa Transcription Error: Connection timed out after 15s during external operation.")
        return None, []
    except urllib.error.URLError as e:
        print(f"Librosa Transcription Error: Network routing failed. {str(e)}")
        return None, []
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
        import socket
        socket.setdefaulttimeout(15.0)

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
    except socket.timeout:
        print("Basic Pitch Error: Connection timed out. Falling back...")
        return extract_pitch_librosa(file_path)
    except urllib.error.URLError as e:
        print(f"Basic Pitch Error: Network routing failed - {str(e)}. Falling back...")
        return extract_pitch_librosa(file_path)
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
