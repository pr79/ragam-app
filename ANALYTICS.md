# ANALYTICS: Ragam App Development

This report summarizes the effort and technical journey of creating the Ragam App using Google Antigravity.

## Global Metrics
- **Total Iterations**: ~65 (Prompt sequences and autonomous corrections)
- **Estimated Development Time**: 140 minutes
- **Successful Modules**: Audio Separation (Demucs), Transcription (Basic Pitch/Librosa), Key Detection, Raga Matching, Harmonic Analysis, Streamlit UI, Windows Packaging.

## Detailed Error Log & Resolution

| Error Type | Frequency | Root Cause | Resolution |
| :--- | :--- | :--- | :--- |
| **NoBackendError** | High | FFmpeg not detected by `pydub`/`librosa` | Created `setup_ffmpeg.py` to auto-download and injected local `bin` into `os.environ["PATH"]`. |
| **PermissionError** | Medium | File locking during PyInstaller builds or output re-writes. | Implemented new build directories (`dist_v2`) and robust `shutil.rmtree` with error handling. |
| **ImportError** | Medium | PyInstaller missing hidden dependencies or version mismatch. | Added `hiddenimports` in `.spec` file and patched `numba` to handle missing functions in frozen state. |
| **Logic/Crash** | Low | Argument mismatch in `mix_stems` (missing directory check). | Added `parent.mkdir(parents=True, exist_ok=True)` before file writes. |
| **Performance** | Low | Deep analysis hanging on long audio files. | Implemented a 60-second processing limit for pitch extraction and MD5-based result caching. |

## Automation Efficacy
- **Autonomous Fix Rate**: ~85% (Antigravity resolved most environment and logic bugs without user intervention).
- **Manual Intervention**: Only required for platform-specific requests (e.g., "Create Mac version") or high-level design changes.


### iOS Safari x Hugging Face Iframe Limitations
- **Problem**: Apple's WebKit engine block Streamlit's media wrappers from executing properly inside Hugging Face Spaces iframes.
- **Attempts**: Base64 embedding and raw HTML5 injection bypass the HTTP network errors but still encounter strict iframe sandboxing.
- **Resolution**: Acknowledged as a platform limitation. A full deployment outside of an iframe (e.g. Heroku, AWS Cloud Run) is required for seamless iOS audio playback.
