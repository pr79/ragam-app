# MASTER PROMPT: Ragam App Reconstruction

Use this prompt to recreate the Ragam App in any GPT-4 class model.

## The Prompt
> "Act as a Senior Python Developer and Music Tech Expert. Create a Streamlit application called 'Ragam App' that performs the following:
> 
> 1. **Audio Separation**: Use `demucs` to split uploads into Vocals, Drums, Bass, and Other. Implement MD5 hashing for caching results.
> 2. **Music Theory**: 
>    - Detect the Tonic (Key) using Librosa Chroma features.
>    - Identify Indian Classical Ragas by comparing the active pitches against the entire 72 Melakarta Raga dictionary.
>    - Provide Arohanam and Avarohanam notation.
> 3. **Transcription**: Extract melodic pitch (MIDI) using `basic-pitch` with a fallback to `librosa.pyin`.
> 4. **Notation**: Convert MIDI to Western (C4, D4) and Carnatic (S, R2, G3) Swaras.
> 5. **Mixer**: Allow the user to select specific stems and generate a new 'Karaoke' or 'Custom' mix file.
> 
> **Architecture Requirements**:
> - Use a modular structure: `app.py` for UI, `src/audio_processor.py` for AI models, `src/music_theory.py` for notations.
> - Handle FFmpeg as a portable dependency in a `bin/` folder.
> - Use `soundfile` for robust audio saving on Windows.
> 
> **Design**: Use a modern layout with custom CSS (glassmorphism, gradient buttons, dark-mode) similar to modern AI audio apps like Suno.ai. Ensure st.session_state is properly cleared via on_change callbacks on file uploaders to prevent stale data."

## Step-by-Step Instructions for AI
1. **Phase 1: Environment Setup**
   - Ask the AI to write a `requirements.txt` including `streamlit`, `demucs`, `basic-pitch`, `librosa`, and `soundfile`.
2. **Phase 2: Core Logic**
   - Provide the AI with a mapping of 12 semitones to Carnatic Swaras.
   - Ask for a 'Raga Database' as a Python dictionary.
3. **Phase 3: Integration**
   - Ask the AI to write the Streamlit UI, ensuring it uses `st.session_state` to prevent data loss on every click.
4. **Phase 4: Packaging**
   - Request a PyInstaller `.spec` file that includes the `bin` folder and `src` modules.

## Agentic AI Workflow
For a more robust and professional implementation, use a multi-agent approach. Each agent should be initialized with a specific role and context.

### 1. Specialized Agent Roles
| Agent Role | Responsibility | Key Deliverables |
| :--- | :--- | :--- |
| **Musicologist Agent** | Create the Raga database from the Melakartha system. Define Swara mappings and Raga rules. | `src/music_theory.py`, Raga JSON/Dictionary. |
| **DSP Engineer Agent** | Implement Demucs for separation and Basic Pitch for transcription. Handle FFmpeg integration. | `src/audio_processor.py`, `setup_ffmpeg.py`. |
| **UI Architect Agent** | Design the Streamlit dashboard. Manage session state, tabs, and file handling logic. | `app.py`. |
| **QA & DevOps Agent** | Perform end-to-end testing. Handle Windows/Mac packaging and documentation. | `TESTING.md`, `setup.py`, `ragam_app.spec`. |

### 2. Interaction Workflow
1. **Initialize Phase**: The **UI Architect** defines the folder structure and shared data schemas (e.g., how the `audio_processor` output should be formatted for the `music_theory` module).
2. **Parallel Implementation**:
   - The **Musicologist Agent** generates a database of all 72 Melakartha Ragas and their Janya (derivative) Ragas, ensuring Swara frequencies and names are accurate.
   - The **DSP Agent** sets up the model inference logic and tests locally with sample MP3s.
3. **Integration**: The **UI Architect** pulls the logic from both agents into the main `app.py`.
4. **Verification**: The **QA Agent** runs the app, uploads various audio types (clean vocals, noisy instruments), and verifies that the Raga detection matches known theory.

### 3. Creating the Raga Database (Agent Task)
Ask the **Musicologist Agent**:
> "Act as a Carnatic Music Expert. Generate a Python dictionary containing all 72 Melakartha Ragas. For each Raga, include its name, index (1-72), Arohanam (ascending scale), and Avarohanam (descending scale) in both Western (C, D, E...) and Carnatic (S, R, G...) notation. Ensure the intervals strictly follow the Melakartha system."
