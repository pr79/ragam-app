"""
Ragam App: Utilities Module
Handles file I/O, directory management, and path resolution.
"""

import os
import shutil
from pathlib import Path
from pydub import AudioSegment

# --- DIRECTORY STRUCTURE ---
# data/
# ├── uploads/    <- Original user files
# └── outputs/    <- Stems, mixes, and analysis results
DATA_DIR = Path("data")
OUTPUT_DIR = DATA_DIR / "outputs"
UPLOAD_DIR = DATA_DIR / "uploads"

def setup_dirs():
    """
    Bootstraps the application by ensuring all required data directories exist.
    Called once during app startup in app.py.
    """
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    UPLOAD_DIR.mkdir(exist_ok=True)

def cleanup_old_files():
    """
    Optional utility to purge old uploads or temporary stems.
    Currently placeholder for future retention policies.
    """
    pass

def get_output_path(category_name, verification_tag=""):
    """
    Generates a directory path for a specific category of output.
    Ex: get_output_path("mixes") -> data/outputs/mixes
    
    Args:
        category_name: Subfolder name (e.g., 'mixes', 'transcriptions').
        verification_tag: Optional suffix for testing.
    """
    base = OUTPUT_DIR / category_name
    if verification_tag:
        base = base.with_name(f"{base.name}_{verification_tag}")
    
    base.mkdir(parents=True, exist_ok=True)
    return base

def save_uploaded_file(uploaded_file):
    """
    Saves a file uploaded via Streamlit to the local 'uploads' directory.
    
    Args:
        uploaded_file: The streamlit UploadedFile object.
        
    Returns:
        Path: The absolute path to the saved file.
    """
    # Ensure filename is sanitized (Streamlit usually does this but we check)
    file_path = UPLOAD_DIR / uploaded_file.name
    
    # Write stream to disk
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    return file_path

def create_preview_audio(wav_path):
    """
    Creates a highly compressed mono MP3 preview of a WAV file to be used in UI visualizers.
    This prevents Streamlit WebSocket crashes caused by sending massive uncompressed audio streams.
    
    Args:
        wav_path (Path or str): Absolute path to the original WAV file.
        
    Returns:
        Path: Absolute path to the compressed MP3 preview.
    """
    wav_path = Path(wav_path)
    mp3_path = wav_path.with_suffix('.preview.mp3')
    
    if not mp3_path.exists():
        try:
            audio = AudioSegment.from_wav(str(wav_path))
            # Mix to mono and compress to 64k to save WebSocket UI payload
            audio = audio.set_channels(1)
            audio.export(str(mp3_path), format="mp3", bitrate="64k")
        except Exception as e:
            print(f"Error creating preview MP3: {e}")
            return wav_path # fallback to original if ffmpeg fails
            
    return mp3_path
