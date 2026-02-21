import json
import raga_dict

content = '''"""
Ragam App: Music Theory Module
Handles Key detection, Raga identification, and Carnatic Swara mapping.

Concepts:
- Tonic (Sa): The reference pitch (0 semitones).
- Swara: Relative melodic intervals in Indian Classical Music.
- Raga: A melodic framework defined by a specific set of ascending (Aro) and 
        descending (Ava) notes.
"""

import numpy as np
import librosa

# --- CARNATIC SWARA MAPPING ---
CARNATIC_SWARAS = {
    0: "S",   # Sa (Tonic)
    1: "R1",  # Shuddha Rishabham (Minor 2nd)
    2: "R2",  # Chatusruti Rishabham (Major 2nd)
    3: "G2",  # Sadharana Gandharam (Minor 3rd)
    4: "G3",  # Antara Gandharam (Major 3rd)
    5: "M1",  # Shuddha Madhyamam (Perfect 4th)
    6: "M2",  # Prati Madhyamam (Augmented 4th)
    7: "P",   # Panchamam (Perfect 5th)
    8: "D1",  # Shuddha Dhaivatam (Minor 6th)
    9: "D2",  # Chatusruti Dhaivatam (Major 6th)
    10: "N2", # Kaisiki Nishadam (Minor 7th)
    11: "N3"  # Kakali Nishadam (Major 7th)
}

# --- RAGA DATABASE ---
''' + 'RAGA_DB = ' + json.dumps(raga_dict.RAGA_DB, indent=4) + '''

WESTERN_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def estimate_key(audio_path, duration=60):
    y, sr = librosa.load(audio_path, duration=duration)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    tonic_idx = int(np.argmax(chroma_mean))
    return tonic_idx, WESTERN_NOTES[tonic_idx], chroma_mean

def identify_raga(chroma_mean, tonic_idx):
    chroma_rel = np.roll(chroma_mean, -tonic_idx)
    chroma_rel = chroma_rel / np.max(chroma_rel)
    captured_scale = np.where(chroma_rel > 0.20)[0].tolist()
    
    best_match = None
    max_overlap = -1
    
    for raga_name, data in RAGA_DB.items():
        scale_indices = data["scale"]
        overlap = len(set(captured_scale).intersection(set(scale_indices)))
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = {
                "name": raga_name,
                "aro": data["aro"],
                "ava": data["ava"]
            }
            
    return best_match, captured_scale

def get_chord_from_chroma(chroma_col):
    templates = {}
    for root in range(12):
        maj = np.zeros(12)
        maj[[root, (root+4)%12, (root+7)%12]] = 1
        templates[f"{WESTERN_NOTES[root]} Maj"] = maj
        
        min_template = np.zeros(12)
        min_template[[root, (root+3)%12, (root+7)%12]] = 1
        templates[f"{WESTERN_NOTES[root]} Min"] = min_template
        
    best_chord = "N/A"
    max_corr = -1
    
    for name, template in templates.items():
        corr = np.dot(chroma_col, template)
        if corr > max_corr:
            max_corr = corr
            best_chord = name
            
    return best_chord

def detect_chords_over_time(audio_path, duration=60):
    y, sr = librosa.load(audio_path, duration=duration)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma = librosa.decompose.nn_filter(chroma, aggregate=np.median, metric="cosine")
    
    chords = []
    times = librosa.frames_to_time(np.arange(chroma.shape[1]), sr=sr)
    
    for i in range(chroma.shape[1]):
        column = chroma[:, i]
        if np.max(column) < 0.1:
            chords.append("N/A")
        else:
            chords.append(get_chord_from_chroma(column))
            
    return times, chords

def note_to_swaras(midi_note, tonic_idx):
    interval = (midi_note - tonic_idx) % 12
    return CARNATIC_SWARAS.get(interval, "?")

def format_swara_sequence(note_events, tonic_idx):
    swaras = []
    for _, _, midi in note_events:
        swaras.append(note_to_swaras(midi, tonic_idx))
    return " ".join(swaras)

def midi_to_western(midi_note):
    octave = (midi_note // 12) - 1
    name = WESTERN_NOTES[midi_note % 12]
    return f"{name}{octave}"
'''

with open('src/music_theory.py', 'w', encoding='utf-8') as f:
    f.write(content)
