# Ragam App Baseline Version

**Version Code:** `🔥 Baseline_v3.0_Global_Framework`
**Description:** Official Architectural Upgrade bringing in Global Framework styling and Resilience patterns.
**Status:** Pristine code with robust timeout handling for heavy inference (Demucs/Basic Pitch). UI injected with dynamic Light/Dark mode Support via Premium Streamlit Theme.

### Contents of this stable release:
- Native `st.audio()` elements for all media wrappers.
- Modern Suno-style CSS interface.
- 72 Melakarta Raga dictionary + Janya ragas.
- Safe `os.path` and FFmpeg dependency routing for portable Windows scaling (`imageio-ffmpeg` bypassing Debian apt-get).
- Decoupled Session State architecture that preserves audio players during parallel backend analysis.

*(To restore the server to this state, revert git/HF commits back to the timestamp of this file).*
