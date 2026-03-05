# Ragam App Baseline Version

**Version Code:** `🔥 Baseline_v4.0_Music_Strategist`
**Description:** Major capability upgrade introducing the Music Strategist Agent's enhanced DSP audio logic and Unified QA validations.
**Status:** Pristine code with robust Streamlit session state tab persistence. UI injected with interactive Audix Waveform players.

### Contents of this stable release:
- **Interactive Waveforms**: Integrated `streamlit-advanced-audio` (Audix) to replace flat linear players.
- **Advanced Track Isolation**: Added Mid/Side and HPSS algorithms to extract Acoustic Guitar, Flute, and Indian Percussion.
- **Persistent UI Layouts**: Refactored logic to sustain Music Analysis results (Calculated Raga, Chords, Notation) when toggling between tabs.
- **Dual Notation Redesign**: Decoupled transcription display into sequential Carnatic Swaras and Western Notation blocks with a dedicated Harmonic Core progression visualizer.
- **Optimized Download UX**: Consolidated output workflows allowing distinct `Custom-Mix.wav` exports and side-by-side stem downloads right below waveforms.

*(To restore the server to this state, revert git/HF commits back to the timestamp of this file).*
