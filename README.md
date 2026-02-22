# 🎵 Ragam App: AI Music Analysis Suite

A state-of-the-art platform for audio separation, karaoke generation, and Indian Classical Music (Raga) identification.

## 🚀 Key Features
- **Source Separation**: 4-stem extraction (Vocals, Drums, Bass, Other) using Facebook's Demucs model.
- **Raga Identification**: Automatic matching for major Carnatic/Hindustani Ragas with Arohanam/Avarohanam.
- **Melodic Transcription**: AI pitch extraction (Basic Pitch) with dual notation (Western & Carnatic Swaras).
- **Custom Mixer**: Real-time track adjustment to create custom karaoke or practice mixes.
- **Speed & Efficiency**: MD5 content-hashing for instant re-runs.

## 📦 Installation (Windows)

### 1. Requirements
- Python 3.10 or 3.11.
- [FFmpeg](https://ffmpeg.org/download.html) (A portable version is auto-downloaded by our setup).

### 2. Quick Start
```bash
# Clone the repository and navigate into it
cd ragam_app

# Install dependencies
pip install -r requirements.txt

# Run the setup script to download models and binaries (if necessary)
python setup_ffmpeg.py
```

### 3. Launching
```bash
streamlit run app.py
```

## 📂 Project Structure
- `app.py`: Main Streamlit UI and app coordinator.
- `src/`: Core logic modules.
  - `audio_processor.py`: Demucs and Basic Pitch integration.
  - `music_theory.py`: Key detection and Raga database.
  - `utils.py`: File system and caching utilities.
- `bin/`: Local binaries (FFmpeg).
- `data/`: Storage for uploads and processed outputs.

## 📊 Maintenance & Analytics
For technical deep-dives into the development process, please refer to:
- [ANALYTICS.md](ANALYTICS.md): Development metrics and iteration logs.
- [MASTER_PROMPT.md](MASTER_PROMPT.md): Instructions to recreate this project.
- [TESTING_AND_LEARNINGS.md](TESTING_AND_LEARNINGS.md): QA reports and key takeaways.

## ☁️ Cloud Deployment (Hugging Face Spaces)
The easiest way to host this app for free is on a **Hugging Face Space** using the Streamlit SDK.
1. Create a Streamlit Space.
2. Ensure you have a `packages.txt` file containing the word `ffmpeg`.
3. Drag and drop the `app.py`, `requirements.txt`, and `src/` folder into the Space.
*(Note: iOS Safari users may experience audio player errors due to Apple's strict iframe security policies on WebKit. A dedicated server host is recommended for flawless mobile performance).*

## 🛠️ Mac OS Support
Mac integration is fully supported via the `mac_build.sh` script, which automatically configures Homebrew, FFmpeg, and Python environments.

---
**Disclaimer**: This app is using heavy AI models. Initial runs for separation and transcription may take 1-2 minutes depending on hardware.
