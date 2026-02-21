import os
import sys
import shutil
import subprocess
import time
import ctypes
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def uninstall():
    # 1. Confirmation
    print("WARNING: This will remove Ragam App and all its data.")
    confirm = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Uninstallation cancelled.")
        input("Press Enter to exit...")
        return

    # 2. Identify Directories
    # Assuming uninstall.exe is in dist/RagamApp/uninstall.exe
    # We want to remove dist/RagamApp
    current_exe = Path(sys.executable)
    app_dir = current_exe.parent
    
    # Verify we are in the expected directory structure to avoid accidents
    if not (app_dir / "run_app.exe").exists() and not (app_dir / "RagamApp.exe").exists():
        print(f"Error: Could not verify application directory at {app_dir}.")
        print("Uninstaller must be run from within the application folder.")
        input("Press Enter to exit...")
        return

    print(f"Uninstalling from: {app_dir}")
    print("Closing application...")
    # Attempt to kill main app if running
    os.system("taskkill /f /im RagamApp.exe >nul 2>&1")
    os.system("taskkill /f /im run_app.exe >nul 2>&1")
    time.sleep(1)

    # 3. Create Self-Deleting Batch Script in Temp
    # This script will:
    # 1. Wait for uninstall.exe to close
    # 2. Delete the app directory
    # 3. Delete itself
    
    cleanup_script_path = Path(os.environ["TEMP"]) / "ragam_cleanup.bat"
    
    batch_content = f"""
@echo off
timeout /t 3 /nobreak > NUL
rmdir /s /q "{app_dir}"
del "%~f0"
"""
    
    with open(cleanup_script_path, "w") as f:
        f.write(batch_content)
        
    print("Cleanup scheduled. The application folder will be removed momentarily.")
    
    # 4. Launch Batch Script and Exit
    subprocess.Popen([str(cleanup_script_path)], shell=True)
    sys.exit(0)

if __name__ == "__main__":
    try:
        uninstall()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
