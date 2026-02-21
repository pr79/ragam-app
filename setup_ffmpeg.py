import os
import zipfile
import urllib.request
from pathlib import Path
import shutil

FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
DEST_DIR = Path("bin")

def download_ffmpeg():
    if (DEST_DIR / "ffmpeg.exe").exists():
        print("FFmpeg already exists.")
        return

    DEST_DIR.mkdir(exist_ok=True)
    zip_path = DEST_DIR / "ffmpeg.zip"
    
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    
    print(f"Downloading FFmpeg from {FFMPEG_URL}...")
    try:
        # Request with headers to avoid basic bot detection? usually github fine.
        urllib.request.urlretrieve(FFMPEG_URL, zip_path)
    except Exception as e:
        print(f"Failed to download: {e}")
        return

    print("Extracting FFmpeg...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract to a temp dir first because the zip contains a subfolder
        zip_ref.extractall(DEST_DIR)
        
    # Move exe to bin root
    # Note: Glob pattern might need adjustment if folder name changes
    # But usually it's consistent.
    subfolders = list(DEST_DIR.glob("ffmpeg-*-win64-gpl"))
    if not subfolders:
         # Fallback search
         subfolders = [x for x in DEST_DIR.iterdir() if x.is_dir()]
         
    if subfolders:
        subfolder = subfolders[0]
        bin_folder = subfolder / "bin"
        
        for exe in bin_folder.glob("*.exe"):
            shutil.move(str(exe), str(DEST_DIR / exe.name))
            
        # Cleanup
        shutil.rmtree(subfolder)
    
    zip_path.unlink()
    
    print("FFmpeg setup complete.")

if __name__ == "__main__":
    download_ffmpeg()
