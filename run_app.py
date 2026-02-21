import os
import sys
import numpy as np

# Shim for Numba compatibility with NumPy 2.x
if not hasattr(np, "trapz"):
    if hasattr(np, "trapezoid"):
        np.trapz = np.trapezoid

import streamlit.web.cli as stcli

# Force PyInstaller to bundle these modules
import src.music_theory
import src.audio_processor
import src.utils

def resolve_path(path):
    if getattr(sys, "frozen", False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

if __name__ == "__main__":
    # Ensure sys.argv has the app script path
    # When running as exe, we need to tell streamlit where the main app file is
    app_path = resolve_path("app.py")
    
    # Fake the argv for streamlit run
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false"
    ]
    
    sys.exit(stcli.main())
