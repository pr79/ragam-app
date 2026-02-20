"""
Ragam App: Utilities Module
Handles file I/O, directory management, and path resolution.
"""

import os
import shutil
from pathlib import Path

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
