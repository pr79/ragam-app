import os
import sys
import shutil
import time
from pathlib import Path

# --- NUMPY 2.x COMPATIBILITY SHIM ---
import numpy as np
if not hasattr(np, "trapz"):
    try:
        np.trapz = np.trapezoid
    except AttributeError:
        pass
# ------------------------------------

# Add local bin to PATH for ffmpeg
sys.path.append(os.getcwd())

from src.audio_processor import separate_audio, mix_stems, transcribe_audio
from src.music_theory import identify_raga, estimate_key, detect_chords_over_time

# User provided path
TEST_FILE = r"C:\Users\prave\Downloads\4K Video Downloader+\O Sajna  Sourendro & Soumyojit   Hariharan   WMD Concert 2022.m4a"

def run_test():
    print("--- Starting End-to-End Backend Test ---")
    
    # 1. Check File Access
    file_path = Path(TEST_FILE)
    if not file_path.exists():
        print(f"ERROR: Test file not found at: {TEST_FILE}")
        return
    print(f"FOUND: Test file: {file_path.name}")
    
    # 2. Test Audio Separation
    print("\n--- Testing Separation (Demucs) ---")
    
    # Run verification logic
    import time

    try:
        # First Run
        start_time = time.time()
        print("Run 1: Separating audio...")
        stems = separate_audio(file_path)
        elapsed_1 = time.time() - start_time
        print(f"Run 1 took {elapsed_1:.2f}s")
        print("Separation Successful!")

        # Second Run (Cache Test)
        print("\n--- Testing Cache (Run 2) ---")
        start_time = time.time()
        stems_2 = separate_audio(file_path)
        elapsed_2 = time.time() - start_time
        print(f"Run 2 took {elapsed_2:.2f}s")

        if elapsed_2 < 5.0:
            print("CACHE VERIFIED: Second run was fast.")
        else:
            print("CACHE WARNING: Second run was slow (did cache miss?).")

        # Verify outputs exist
        for name, path in stems.items():
            if path.exists():
                print(f"   - {name}: {path} (Exists)")
            else:
                print(f"   - {name}: {path} (MISSING!)")
    except Exception as e:
        print(f"Separation Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. Test Mixing
    print("\n--- Testing Mixing ---")
    try:
        # Mix vocals and drums as a test
        mix_targets = [stems["vocals"], stems["drums"]]
        output_mix = Path("test_mix.wav")
        mixed_path = mix_stems(mix_targets, output_mix)
        if mixed_path and mixed_path.exists():
             print(f"Mixing Successful: {mixed_path}")
        else:
             print("Mixing returned None or file missing.")
    except Exception as e:
        print(f"Mixing Failed: {e}")
        
    # 4. Test Analysis (Vocals)
    print("\n--- Testing Analysis (Vocals) ---")
    vocab_path = stems["vocals"]
    try:
        # Key
        key = estimate_key(vocab_path)
        print(f"Key Estimated: {key}")
        
        # Raga
        tonic_idx = key[0]
        chroma_mean = key[2]
        raga_info, _ = identify_raga(chroma_mean, tonic_idx)
        if raga_info:
            print(f"Raga Identified: {raga_info['name']}")
            print(f"  Aro: {raga_info['aro']}")
            print(f"  Ava: {raga_info['ava']}")
        else:
            print("Raga Identified: None")
        
        # Chords
        chords = detect_chords_over_time(vocab_path)
        print(f"Chords Detected: {len(chords)} events")
        
    except Exception as e:
        print(f"Analysis Failed: {e}")
        import traceback
        traceback.print_exc()

    # 5. Test Carnatic Notation (New Feature)
    print("\n--- Testing Carnatic Notation Logic ---")
    try:
        # Test 1: Note to Swara Mapping
        from src.music_theory import note_to_swaras, format_swara_sequence
        # C Major Scale (C D E F G A B) with C as Tonic (0)
        # Should be S R2 G3 M1 P D2 N3
        test_notes = [60, 62, 64, 65, 67, 69, 71] # C4, D4, E4, F4, G4, A4, B4
        tonic = 0 # C
        expected_swaras = "S R2 G3 M1 P D2 N3"
        
        # Test tuple format for formatter
        note_events = [(0, 1, n) for n in test_notes]
        result_swara = format_swara_sequence(note_events, tonic)
        print(f"Swara Mapping Test: {'PASS' if result_swara == expected_swaras else 'FAIL'}")
        print(f"  Expected: {expected_swaras}")
        print(f"  Got:      {result_swara}")
        
        # Test 2: Pitch Extraction (Librosa Fallback)
        print("\n--- Testing Librosa Pitch Extraction ---")
        from src.audio_processor import extract_pitch_librosa
        # Use vocals stem from previous step
        vocab_path = stems["vocals"]
        path, notes = extract_pitch_librosa(vocab_path)
        
        if len(notes) > 0:
            print(f"Pitch Extraction Successful: Found {len(notes)} note events.")
            print(f"First 5 notes: {[n[2] for n in notes[:5]]}")
        else:
            print("Pitch Extraction Warning: No notes found (might be silent/short track).")
            
    except Exception as e:
        print(f"Notation Test Failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    run_test()
