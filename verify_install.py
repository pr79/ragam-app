import sys
print(f"Python: {sys.version}")

try:
    print("Importing torch...")
    import torch
    print(f"Torch version: {torch.__version__}")
    
    print("Importing torchaudio...")
    import torchaudio
    print(f"Torchaudio version: {torchaudio.__version__}")
    
    print("Importing torchcodec...")
    import torchcodec
    print(f"Torchcodec version: {torchcodec.__version__}")

    print("Importing demucs...")
    import demucs.separate
    print("Demucs imported successfully.")
    
    print("Importing soundfile...")
    import soundfile
    print("Soundfile imported successfully.")
    
    print("Importing numpy...")
    import numpy
    print("Numpy imported successfully.")
    
    print("Importing streamlit...")
    import streamlit
    print("Streamlit imported successfully.")
    
    print("\n✅ All critical dependencies are installed and loadable.")

except ImportError as e:
    print(f"\n❌ MISSING DEPENDENCY: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    sys.exit(1)
