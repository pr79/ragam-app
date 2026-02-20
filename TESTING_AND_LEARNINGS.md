# TESTING & KEY LEARNINGS

## Testing Strategy

### 1. Automated Verification
- **`test_end_to_end.py`**: A comprehensive script that simulates a full user journey:
    - Checks for FFmpeg availability.
    - Runs separation on a test file.
    - Verifies that all 4 stems are generated.
    - Runs the Raga identification and pitch extraction logic.
    - Asserts that output files and MIDI notes exist.

### 2. Manual Verification
- **Streamlit UI Testing**: Iterative testing of widget interactions, state persistence, and error message styling.
- **Build Verification**: Running the final `RagamApp.exe` in a clean environment to ensure portable dependencies (FFmpeg) work.

---

## Key Learnings

### 1. The "FFmpeg Bottleneck"
- **Issue**: Almost all Python audio libraries (Librosa, Pydub, Soundfile, Demucs) rely on FFmpeg, but assume it's globally installed.
- **Learning**: For portable apps, always include a local binary and programmatically inject it into `os.environ["PATH"]` at the very first line of `app.py`.

### 2. State Management is King
- **Issue**: Streamlit re-runs the entire script on every user interaction, which can wipe variables or trigger heavy AI processing multiple times.
- **Learning**: Strategic use of `st.session_state` and content-based caching (MD5) is mandatory for audio apps to feel "snappy."

### 3. Dependency Fragility
- **Issue**: Libraries like `numba` and `torchaudio` often fail when "frozen" inside an EXE due to dynamic loading of C-libraries.
- **Learning**: Using `soundfile` as an I/O backend is much more stable than `torchaudio` for Windows packaging. Manual patching (Monkeypatching) of library functions is a powerful tool to bridge these gaps.

### 4. AI-Agent Collaboration
- **Issue**: The agent can move very fast, sometimes out-pacing the user's manual check.
- **Learning**: Structuring tasks into clear 'Verification' phases helps the user keep track of what is truly "done" vs "implemented."
