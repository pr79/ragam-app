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
from pathlib import Path

# --- BOOTSTRAP: FFmpeg & Environment ---
# We inject the local 'bin' folder (containing ffmpeg.exe) into the PATH 
# variable so that libraries like 'pydub' and 'demucs' can find it.
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle
    base_path = Path(sys.executable).parent
else:
    # Running as a Python script
    base_path = Path(__file__).parent.resolve()

local_bin = (base_path / "bin").resolve()

if local_bin.exists():
    # Prepend to PATH to ensure our bundled FFmpeg takes precedence
    os.environ["PATH"] = str(local_bin) + os.pathsep + os.environ["PATH"]
else:
    # This might happen in development if setup_ffmpeg.py hasn't run
    print(f"WARNING: 'bin' folder not found at {local_bin}")

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
    /* Global Background and Fonts */
    .stApp {
        background: linear-gradient(135deg, #0f172a, #1e1b4b, #2e1065);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    /* Cards and Containers (Glassmorphism) */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #8b5cf6, #d946ef);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5);
    }
    
    /* File Uploader override */
    [data-testid="stFileUploadDropzone"] {
        background: rgba(255, 255, 255, 0.02);
        border: 2px dashed rgba(139, 92, 246, 0.4);
        border-radius: 16px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
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
from src.utils import UPLOAD_DIR, setup_dirs, save_uploaded_file, get_output_path

# Initialize directory structure (uploads, outputs, etc.)
setup_dirs()

# --- SESSION STATE INITIALIZATION ---
# Streamlit keeps the state in 'st.session_state'. 
# We initialize keys to avoid 'KeyError'.
if "stems" not in st.session_state:
    st.session_state.stems = {}           # Dict: {stem_name: local_path}
if "original_audio" not in st.session_state:
    st.session_state.original_audio = None # Path to uploaded file

def reset_session_state():
    """Callback fired when a new file is uploaded to prevent old stems from showing."""
    st.session_state.stems = {}
    st.session_state.analyze_target = None

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
    
    st.audio(file_path, format='audio/wav')
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
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Source Separation")
        st.write("Split song into Vocals, Bass, Drums, and Others.")
        if st.button("Run Demucs Separator", use_container_width=True):
            with st.spinner("Processing audio... This uses MD5 caching for speed."):
                try:
                    start_time = time.time()
                    stem_paths = separate_audio(file_path)
                    elapsed = time.time() - start_time
                    st.session_state.stems = stem_paths
                    
                    # Logic to identify if we used cache
                    if elapsed < 2.0:
                        st.success(f"Restored from Cache ({elapsed:.2f}s)!")
                    else:
                        st.success(f"Separation Complete ({elapsed:.2f}s)!")
                except Exception as e:
                    st.error(f"Separation failed: {e}")
                    st.code(traceback.format_exc())

    with col2:
        st.subheader("2. Instant Analysis")
        st.write("Analyze the full track without separation.")
        if st.button("Analyze Original", use_container_width=True):
             # Trigger analysis without changing dropdown focus
             st.session_state.analyze_target = "Original"

    # --- SECTION 2: STEM MIXER ---
    if st.session_state.stems:
        st.divider()
        st.subheader("🎛️ Stem Mixer")
        st.info("Adjust which tracks to include in your custom mix (e.g., for Karaoke).")
        
        with st.container(border=True):
            stems_list = list(st.session_state.stems.items())
            cols = st.columns(len(stems_list))
            mix_selections = {}
            
            # Interactive stem preview and selection
            for j, (stem_name, stem_path) in enumerate(stems_list):
                if stem_name == "Custom Mix": continue # Don't mix the mix
                with cols[j]:
                    st.markdown(f"**{stem_name.title()}**")
                    st.audio(str(stem_path), format="audio/wav")
                    mix_selections[stem_name] = st.checkbox(
                        "Include", value=True, key=f"mix_{stem_name}"
                    )

            # Execution of the mixer
            if st.button("Generate & Play Custom Mix", use_container_width=True):
                selected_paths = [
                    st.session_state.stems[s] 
                    for s, active in mix_selections.items() if active
                ]
                if selected_paths:
                    # Output is saved to 'data/outputs/mixes'
                    output_mix = get_output_path("mixes") / "custom_mix.wav"
                    mix_stems(selected_paths, output_mix)
                    st.audio(str(output_mix), format="audio/wav")
                    st.session_state.stems["Custom Mix"] = str(output_mix) 
                else:
                    st.warning("Please select at least one track to mix.")

    st.divider()
    
    # --- SECTION 3: MUSIC THEORY ANALYSIS ---
    st.subheader("🎼 Raga & Notation Analysis")
    st.write("Identify Ragas, transcribe notes, and detect chord progressions.")
    
    # Track selection for analysis (usually Vocals is best for Raga identification)
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
    
    # Conditional logic to trigger analysis from multiple locations
    if analyze_clicked or st.session_state.get("analyze_target"):
        if st.session_state.get("analyze_target") == "Original":
             target_stem = "Original"
             st.session_state.analyze_target = None
             
        # Resolve target file path
        target_path = (
            st.session_state.original_audio 
            if target_stem == "Original" 
            else st.session_state.stems[target_stem]
        )
        
        with st.status(f"Processing '{target_stem}'...", expanded=True) as status:
            # Step A: Estimate Tonic (Sa)
            st.write("Detecting Tonic / Key...")
            tonic_idx, tonic_name, chroma_mean = estimate_key(target_path)
            
            # Step B: Identify Raga
            st.write("Matching Scale against Raga Database...")
            raga_info, scale_indices = identify_raga(chroma_mean, tonic_idx)
            
            # Step C: Transcription (AI Pitch Extraction)
            st.write("Transcribing Melodic Line...")
            mid_path, note_events = transcribe_audio(target_path)
            
            # Step D: Harmonic Analysis (Chords)
            st.write("Analyzing Harmony / Chords...")
            times, chords = detect_chords_over_time(target_path, duration=30)
            
            status.update(label="Analysis Done!", state="complete", expanded=True)

        # --- RESULTS LAYOUT ---
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.info(f"**Detected Tonic (Sa)**: {tonic_name}")
            if raga_info:
                st.success(f"**Raga Match**: {raga_info['name']}")
                st.caption(f"**Arohanam**: {raga_info['aro']}")
                st.caption(f"**Avarohanam**: {raga_info['ava']}")
            else:
                 st.warning("**Raga**: No confident match found in current database.")

        with res_col2:
             # Unique chord sequence for the intro segment
             chord_seq = " ➔ ".join([
                 c for i, c in enumerate(chords) 
                 if i == 0 or c != chords[i-1]
             ])
             st.markdown("**Core Chord Progression**")
             st.text_area("Progression", chord_seq, height=100)

        # Melodic Data Display
        if len(note_events) > 0:
            st.markdown("### 🎵 Melodic Transcription (Swaras)")
            
            # Show a readable swara sequence (first 30 notes)
            swara_str = format_swara_sequence(note_events[:30], tonic_idx)
            st.code(swara_str, language="text")
            
            with st.expander("Detailed Pitch Data (CSV Table)"):
                note_data = []
                for start, end, midi_note in note_events: 
                    western = midi_to_western(midi_note)
                    carnatic = note_to_swaras(midi_note, tonic_idx)
                    note_data.append({
                        "Time (s)": f"{start:.2f}-{end:.2f}",
                        "Western": western,
                        "Carnatic": carnatic
                    })
                st.dataframe(note_data, use_container_width=True)
        else:
             st.info("No melodic notes detected in this selection.")
