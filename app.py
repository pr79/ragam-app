"""
Ragam App: AI Music Separator & Raga Identifier
Main Entry Point (Streamlit UI)

Architecture Overview:
- Frontend: Streamlit (Web-based UI)
- Backend: Specialized modules in 'src/' for audio processing and music theory.
- State Management: Uses st.session_state for persistence across re-runs.
- FFmpeg: Critical dependency handled via PATH injection.
"""

import streamlit as st
import os
import sys
import time
import traceback
import base64
import logging
import streamlit.components.v1 as components
from pathlib import Path
from config.config import LOG_LEVEL, LOG_DIR, SUPPORTED_AUDIO_FORMATS, FFMPEG_BIN_DIR

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)-5s] %(name)s — %(message)s")
log = logging.getLogger(__name__)

# --- BOOTSTRAP: FFmpeg & Environment ---
# We inject the local 'bin' folder (containing ffmpeg.exe) into the PATH 
# variable so that libraries like 'pydub' and 'demucs' can find it.
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle
    base_path = Path(sys.executable).parent
else:
    # Running as a Python script
    base_path = Path(__file__).parent.resolve()

local_bin = (base_path / FFMPEG_BIN_DIR).resolve()

if local_bin.exists():
    # Prepend to PATH to ensure our bundled FFmpeg takes precedence
    os.environ["PATH"] = str(local_bin) + os.pathsep + os.environ["PATH"]
else:
    # This might happen in development if setup_ffmpeg.py hasn't run
    log.warning("'bin' folder not found at %s — ffmpeg may fail", local_bin)

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="Ragam App", 
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN UI CSS INJECTION ---
st.markdown("""
<style>
/* Gradient Header Text */
.header-text {
    font-family: 'Inter', sans-serif;
    background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 3rem;
    margin-bottom: 20px;
}

/* Premium Button UX */
.stButton>button {
    width: 100%;
    border-radius: 8px;
    transition: 0.3s;
    font-weight: 600;
}

/* 3D Float Hover Effect */
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}

/* Reference Card Styling */
.ref-card {
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 10px;
    border-left: 4px solid #FF416C;
}
</style>
""", unsafe_allow_html=True)

# --- INTERNAL IMPORTS ---
# Imports are done after PATH setup to ensure sub-dependencies find FFmpeg
import src.audio_processor
from src.audio_processor import separate_audio, mix_stems, transcribe_audio
import src.music_theory
from src.music_theory import (
    estimate_key, identify_raga, detect_chords_over_time, 
    note_to_swaras, midi_to_western, format_swara_sequence
)
import src.utils
from src.utils import UPLOAD_DIR, setup_dirs, save_uploaded_file, get_output_path, create_preview_audio

# Initialize directory structure (uploads, outputs, etc.)
setup_dirs()

# --- SESSION STATE INITIALIZATION ---
# Streamlit keeps the state in 'st.session_state'. 
# We initialize keys to avoid 'KeyError'.
if "stems" not in st.session_state:
    st.session_state.stems = {}           # Dict: {stem_name: local_path}
if "original_audio" not in st.session_state:
    st.session_state.original_audio = None # Path to uploaded file
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

def reset_session_state():
    """Callback fired when a new file is uploaded to prevent old stems from showing."""
    st.session_state.stems = {}
    st.session_state.analyze_target = None
    st.session_state.analysis_results = None

def render_wavesurfer(audio_path, key):
    preview_path = create_preview_audio(audio_path)
    try:
        with open(preview_path, "rb") as f:
            b64_audio = base64.b64encode(f.read()).decode()
    except Exception as e:
        st.error(f"Failed to load audio for preview: {e}")
        return

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/wavesurfer.js@7/dist/wavesurfer.min.js"></script>
        <style>
            body { font-family: sans-serif; margin: 0; padding: 0; background: transparent; overflow: hidden; }
            #waveform-KEY { width: 100%; height: 80px; margin-bottom: 5px; }
            .controls { display: flex; align-items: center; gap: 10px; }
            button { background: #FF416C; color: white; border: none; padding: 5px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 13px; }
            button:hover { background: #FF4B2B; }
            #time-KEY { font-size: 13px; color: #555; }
        </style>
    </head>
    <body>
        <div id="waveform-KEY"></div>
        <div class="controls">
            <button id="play-KEY">Play / Pause</button>
            <span id="time-KEY">0:00 / 0:00</span>
        </div>
        
        <script>
            const wavesurfer = WaveSurfer.create({
                container: '#waveform-KEY',
                waveColor: '#ff7b93',
                progressColor: '#FF416C',
                barWidth: 2,
                barRadius: 2,
                cursorColor: '#FF4B2B',
                height: 80,
                normalize: true,
                url: 'data:audio/mp3;base64,B64_AUDIO_DATA'
            });

            const btn = document.getElementById('play-KEY');
            const timeEl = document.getElementById('time-KEY');

            wavesurfer.on('interaction', () => wavesurfer.play());
            btn.addEventListener('click', () => wavesurfer.playPause());
            
            const formatTime = (seconds) => {
                const mins = Math.floor(seconds / 60);
                const secs = Math.floor(seconds % 60);
                return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
            };

            wavesurfer.on('audioprocess', () => {
                timeEl.textContent = formatTime(wavesurfer.getCurrentTime()) + ' / ' + formatTime(wavesurfer.getDuration());
            });
            
            wavesurfer.on('ready', () => {
                timeEl.textContent = '0:00 / ' + formatTime(wavesurfer.getDuration());
            });
        </script>
    </body>
    </html>
    """
    html = html_template.replace("KEY", key).replace("B64_AUDIO_DATA", b64_audio)
    components.html(html, height=130)

# --- UI HEADER ---
st.title("🎵 AI Music Separator & Raga Identifier")
st.markdown("""
Extract vocals and instruments, create karaoke mixes, and analyze Indian Classical Ragas 
using state-of-the-art AI models (Demucs, Basic Pitch).
""")

# --- SECTION 1: FILE UPLOAD ---
# Allowed formats cover common audio codecs
uploaded_file = st.file_uploader(
    "Upload a Song (MP3, WAV, etc.)", 
    type=["mp3", "wav", "m4a", "flac", "ogg"],
    on_change=reset_session_state
)

if uploaded_file is not None:
    # Persistent storage of the uploaded file
    file_path = save_uploaded_file(uploaded_file)
    st.session_state.original_audio = file_path
    
    render_wavesurfer(str(file_path), key="original")
    st.success(f"File ready: {uploaded_file.name}")

    # --- SIDEBAR CONTROLS ---
    with st.sidebar:
        st.header("⚙️ App Controls")
        if st.button("Reset Session", type="primary", help="Clears all cache and resets state"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
        st.divider()
        st.markdown("**System Status**")
        if st.session_state.get("stems"):
            st.success("Stems Separated")
        else:
            st.info("Waiting for Separation...")

    # --- MAIN ACTION AREA ---
    tab_sep, tab_ana = st.tabs(["🎛️ Separate Tracks", "🎼 Analyze Music"])
    
    with tab_sep:
        st.subheader("🎛️ Source Separation & Mixing")
        st.write("Split song into Vocals, Bass, Drums, Piano, Guitar, Flute, and Percussion.")
        
        btn_col, _ = st.columns([1, 2])
        with btn_col:
            run_separator = st.button("Run AI Separator (Demucs 6s + DSP)", use_container_width=True, type="primary")
            
        if run_separator:
            with st.spinner("Processing audio... This uses MD5 caching for speed."):
                try:
                    start_time = time.time()
                    stem_paths = separate_audio(file_path)
                    elapsed = time.time() - start_time
                    st.session_state.stems = stem_paths
                    
                    if elapsed < 2.0:
                        st.success(f"Restored from Cache ({elapsed:.2f}s)!")
                    else:
                        st.success(f"Separation Complete ({elapsed:.2f}s)!")
                except Exception as e:
                    st.error(f"Separation failed: {e}")
                    st.code(traceback.format_exc())

        if st.session_state.stems:
            st.divider()
            st.subheader("🎚️ Separated Tracks")
            st.info("Adjust which tracks to include in your custom mix (e.g., for Karaoke). Download individual tracks via the buttons.")
            
            @st.fragment
            def render_stem_row(stem_name, stem_path):
                with st.container(border=True):
                    # Responsive columns for each track row
                    row_col1, row_col2, row_col3 = st.columns([1.5, 4, 1])
                    
                    with row_col1:
                        display_name = stem_name.replace("_", " ").title()
                        st.markdown(f"**{display_name}**")
                        st.checkbox("Include in Mix", value=True, key=f"mix_{stem_name}")
                        
                    with row_col2:
                        render_wavesurfer(str(stem_path), key=f"stem_{stem_name}")
                        
                    with row_col3:
                        with open(stem_path, "rb") as f:
                            st.download_button(
                                label="⬇️ Download",
                                data=f,
                                file_name=f"{stem_name}.wav",
                                mime="audio/wav",
                                key=f"dl_{stem_name}",
                                use_container_width=True
                            )

            for stem_name, stem_path in list(st.session_state.stems.items()):
                if stem_name == "Custom Mix": continue
                render_stem_row(stem_name, stem_path)
                            
            st.markdown("---")
            if st.button("Generate & Play Custom Mix", use_container_width=True):
                selected_paths = [
                    st.session_state.stems[s] 
                    for s in st.session_state.stems.keys() 
                    if s != "Custom Mix" and st.session_state.get(f"mix_{s}", True)
                ]
                if selected_paths:
                    output_mix = get_output_path("mixes") / "custom_mix.wav"
                    mix_stems(selected_paths, output_mix)
                    st.session_state.stems["Custom Mix"] = str(output_mix) 
                else:
                    st.warning("Please select at least one track to mix.")
                    
            if "Custom Mix" in st.session_state.stems:
                st.markdown("### 🎧 Your Custom Mix")
                custom_mix_path = st.session_state.stems["Custom Mix"]
                with st.container(border=True):
                    row_col1, row_col2, row_col3 = st.columns([1.5, 4, 1])
                    with row_col1:
                        st.markdown("**Custom Mix**")
                    with row_col2:
                        render_wavesurfer(str(custom_mix_path), key="custom_mix")
                    with row_col3:
                        with open(custom_mix_path, "rb") as f:
                            st.download_button(
                                label="⬇️ Download Mix",
                                data=f,
                                file_name="Custom-Mix.wav",
                                mime="audio/wav",
                                key="dl_custom_mix",
                                use_container_width=True
                            )

    with tab_ana:
        # --- SECTION 3: MUSIC THEORY ANALYSIS ---
        st.subheader("🎼 Raga & Notation Analysis")
        st.write("Identify Ragas, transcribe notes, and detect chord progressions.")
        
        # Track selection for analysis
        analysis_options = []
        if st.session_state.original_audio:
            analysis_options.append("Original")
        if st.session_state.stems:
            analysis_options.extend([
                k for k in st.session_state.stems.keys() 
                if k not in ["Original", "Custom Mix"]
            ])
            
        col_opt, col_go = st.columns([3, 1])
        with col_opt:
            target_stem = st.selectbox(
                "Track to Analyze", analysis_options, 
                index=0, label_visibility="collapsed"
            )
        with col_go:
            analyze_clicked = st.button("Run Analysis", type="primary", use_container_width=True)
        
        if analyze_clicked:
            target_path = (
                st.session_state.original_audio 
                if target_stem == "Original" 
                else st.session_state.stems[target_stem]
            )
            
            with st.status(f"Processing '{target_stem}'...", expanded=True) as status:
                st.write("Detecting Tonic / Key...")
                tonic_idx, tonic_name, chroma_mean = estimate_key(target_path)
                
                st.write("Matching Scale against Raga Database...")
                raga_info, scale_indices = identify_raga(chroma_mean, tonic_idx)
                
                st.write("Transcribing Melodic Line...")
                mid_path, note_events = transcribe_audio(target_path)
                
                st.write("Analyzing Harmony / Chords...")
                times, chords = detect_chords_over_time(target_path, duration=30)
                
                st.session_state.analysis_results = {
                    "tonic_name": tonic_name,
                    "tonic_idx": tonic_idx,
                    "raga_info": raga_info,
                    "chords": chords,
                    "note_events": note_events,
                    "target_stem": target_stem
                }
                
                status.update(label="Analysis Done!", state="complete", expanded=True)

        results = st.session_state.analysis_results
        if results:
            st.markdown("---")
            st.markdown(f"**Analysis Results for Track:** `{results['target_stem']}`")
            
            # --- RESULTS LAYOUT ---
            st.info(f"**Detected Tonic (Sa)**: {results['tonic_name']}")
            
            if results['raga_info']:
                st.success(f"**Raga Match**: {results['raga_info']['name']}")
                raga_col1, raga_col2 = st.columns(2)
                with raga_col1:
                    st.warning(f"**Arohanam** (Ascending)\n\n{results['raga_info']['aro']}")
                with raga_col2:
                    st.warning(f"**Avarohanam** (Descending)\n\n{results['raga_info']['ava']}")
            else:
                st.warning("**Raga**: No confident match found in current database.")

            chord_seq = " ➔ ".join([
                c for i, c in enumerate(results['chords']) 
                if i == 0 or c != results['chords'][i-1]
            ])
            st.markdown("### 🎹 Harmonic Core")
            st.markdown("**Core Chord Progression**")
            st.info(chord_seq)

            # Melodic Data Display
            if len(results['note_events']) > 0:
                st.markdown("### 🎵 Melodic Transcription")
                
                carnatic_swaras = []
                western_notes = []
                for start, end, midi in results['note_events'][:30]:
                    western_notes.append(midi_to_western(midi))
                    carnatic_swaras.append(note_to_swaras(midi, results['tonic_idx']))
                
                st.markdown("**Carnatic Notations**")
                st.success("   ".join(carnatic_swaras))
                
                st.markdown("**Western Notations**")
                st.success("   ".join(western_notes))
                
                with st.expander("Detailed Pitch Data (CSV Table)"):
                    note_data = []
                    for start, end, midi_note in results['note_events']: 
                        western = midi_to_western(midi_note)
                        carnatic = note_to_swaras(midi_note, results['tonic_idx'])
                        note_data.append({
                            "Time (s)": f"{start:.2f}-{end:.2f}",
                            "Western Note": western,
                            "Carnatic Swara": carnatic
                        })
                    st.dataframe(note_data, use_container_width=True)
            else:
                 st.info("No melodic notes detected in this selection.")
