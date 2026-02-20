"""
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
RAGA_DB = {
    "1. Kanakangi": {
        "scale": [
            0,
            1,
            2,
            5,
            7,
            8,
            9
        ],
        "aro": "S R1 G1 M1 P D1 N1 S",
        "ava": "S N1 D1 P M1 G1 R1 S"
    },
    "2. Ratnangi": {
        "scale": [
            0,
            1,
            2,
            5,
            7,
            8,
            10
        ],
        "aro": "S R1 G1 M1 P D1 N2 S",
        "ava": "S N2 D1 P M1 G1 R1 S"
    },
    "3. Ganamurti": {
        "scale": [
            0,
            1,
            2,
            5,
            7,
            8,
            11
        ],
        "aro": "S R1 G1 M1 P D1 N3 S",
        "ava": "S N3 D1 P M1 G1 R1 S"
    },
    "4. Vanaspati": {
        "scale": [
            0,
            1,
            2,
            5,
            7,
            9,
            10
        ],
        "aro": "S R1 G1 M1 P D2 N2 S",
        "ava": "S N2 D2 P M1 G1 R1 S"
    },
    "5. Manavati": {
        "scale": [
            0,
            1,
            2,
            5,
            7,
            9,
            11
        ],
        "aro": "S R1 G1 M1 P D2 N3 S",
        "ava": "S N3 D2 P M1 G1 R1 S"
    },
    "6. Tanarupi": {
        "scale": [
            0,
            1,
            2,
            5,
            7,
            10,
            11
        ],
        "aro": "S R1 G1 M1 P D3 N3 S",
        "ava": "S N3 D3 P M1 G1 R1 S"
    },
    "7. Senavati": {
        "scale": [
            0,
            1,
            3,
            5,
            7,
            8,
            9
        ],
        "aro": "S R1 G2 M1 P D1 N1 S",
        "ava": "S N1 D1 P M1 G2 R1 S"
    },
    "8. Hanumatodi": {
        "scale": [
            0,
            1,
            3,
            5,
            7,
            8,
            10
        ],
        "aro": "S R1 G2 M1 P D1 N2 S",
        "ava": "S N2 D1 P M1 G2 R1 S"
    },
    "9. Dhenuka": {
        "scale": [
            0,
            1,
            3,
            5,
            7,
            8,
            11
        ],
        "aro": "S R1 G2 M1 P D1 N3 S",
        "ava": "S N3 D1 P M1 G2 R1 S"
    },
    "10. Natakapriya": {
        "scale": [
            0,
            1,
            3,
            5,
            7,
            9,
            10
        ],
        "aro": "S R1 G2 M1 P D2 N2 S",
        "ava": "S N2 D2 P M1 G2 R1 S"
    },
    "11. Kokilapriya": {
        "scale": [
            0,
            1,
            3,
            5,
            7,
            9,
            11
        ],
        "aro": "S R1 G2 M1 P D2 N3 S",
        "ava": "S N3 D2 P M1 G2 R1 S"
    },
    "12. Rupavati": {
        "scale": [
            0,
            1,
            3,
            5,
            7,
            10,
            11
        ],
        "aro": "S R1 G2 M1 P D3 N3 S",
        "ava": "S N3 D3 P M1 G2 R1 S"
    },
    "13. Gayakapriya": {
        "scale": [
            0,
            1,
            4,
            5,
            7,
            8,
            9
        ],
        "aro": "S R1 G3 M1 P D1 N1 S",
        "ava": "S N1 D1 P M1 G3 R1 S"
    },
    "14. Vakulabharanam": {
        "scale": [
            0,
            1,
            4,
            5,
            7,
            8,
            10
        ],
        "aro": "S R1 G3 M1 P D1 N2 S",
        "ava": "S N2 D1 P M1 G3 R1 S"
    },
    "15. Mayamalavagowla": {
        "scale": [
            0,
            1,
            4,
            5,
            7,
            8,
            11
        ],
        "aro": "S R1 G3 M1 P D1 N3 S",
        "ava": "S N3 D1 P M1 G3 R1 S"
    },
    "16. Chakravakam": {
        "scale": [
            0,
            1,
            4,
            5,
            7,
            9,
            10
        ],
        "aro": "S R1 G3 M1 P D2 N2 S",
        "ava": "S N2 D2 P M1 G3 R1 S"
    },
    "17. Suryakantam": {
        "scale": [
            0,
            1,
            4,
            5,
            7,
            9,
            11
        ],
        "aro": "S R1 G3 M1 P D2 N3 S",
        "ava": "S N3 D2 P M1 G3 R1 S"
    },
    "18. Hatakambari": {
        "scale": [
            0,
            1,
            4,
            5,
            7,
            10,
            11
        ],
        "aro": "S R1 G3 M1 P D3 N3 S",
        "ava": "S N3 D3 P M1 G3 R1 S"
    },
    "19. Jhankaradhvani": {
        "scale": [
            0,
            2,
            3,
            5,
            7,
            8,
            9
        ],
        "aro": "S R2 G2 M1 P D1 N1 S",
        "ava": "S N1 D1 P M1 G2 R2 S"
    },
    "20. Natabhairavi": {
        "scale": [
            0,
            2,
            3,
            5,
            7,
            8,
            10
        ],
        "aro": "S R2 G2 M1 P D1 N2 S",
        "ava": "S N2 D1 P M1 G2 R2 S"
    },
    "21. Keeravani": {
        "scale": [
            0,
            2,
            3,
            5,
            7,
            8,
            11
        ],
        "aro": "S R2 G2 M1 P D1 N3 S",
        "ava": "S N3 D1 P M1 G2 R2 S"
    },
    "22. Kharaharapriya": {
        "scale": [
            0,
            2,
            3,
            5,
            7,
            9,
            10
        ],
        "aro": "S R2 G2 M1 P D2 N2 S",
        "ava": "S N2 D2 P M1 G2 R2 S"
    },
    "23. Gourimanohari": {
        "scale": [
            0,
            2,
            3,
            5,
            7,
            9,
            11
        ],
        "aro": "S R2 G2 M1 P D2 N3 S",
        "ava": "S N3 D2 P M1 G2 R2 S"
    },
    "24. Varunapriya": {
        "scale": [
            0,
            2,
            3,
            5,
            7,
            10,
            11
        ],
        "aro": "S R2 G2 M1 P D3 N3 S",
        "ava": "S N3 D3 P M1 G2 R2 S"
    },
    "25. Mararanjani": {
        "scale": [
            0,
            2,
            4,
            5,
            7,
            8,
            9
        ],
        "aro": "S R2 G3 M1 P D1 N1 S",
        "ava": "S N1 D1 P M1 G3 R2 S"
    },
    "26. Charukesi": {
        "scale": [
            0,
            2,
            4,
            5,
            7,
            8,
            10
        ],
        "aro": "S R2 G3 M1 P D1 N2 S",
        "ava": "S N2 D1 P M1 G3 R2 S"
    },
    "27. Sarasangi": {
        "scale": [
            0,
            2,
            4,
            5,
            7,
            8,
            11
        ],
        "aro": "S R2 G3 M1 P D1 N3 S",
        "ava": "S N3 D1 P M1 G3 R2 S"
    },
    "28. Harikambhoji": {
        "scale": [
            0,
            2,
            4,
            5,
            7,
            9,
            10
        ],
        "aro": "S R2 G3 M1 P D2 N2 S",
        "ava": "S N2 D2 P M1 G3 R2 S"
    },
    "29. Dheerasankarabharanam": {
        "scale": [
            0,
            2,
            4,
            5,
            7,
            9,
            11
        ],
        "aro": "S R2 G3 M1 P D2 N3 S",
        "ava": "S N3 D2 P M1 G3 R2 S"
    },
    "30. Naganandini": {
        "scale": [
            0,
            2,
            4,
            5,
            7,
            10,
            11
        ],
        "aro": "S R2 G3 M1 P D3 N3 S",
        "ava": "S N3 D3 P M1 G3 R2 S"
    },
    "31. Yagapriya": {
        "scale": [
            0,
            3,
            4,
            5,
            7,
            8,
            9
        ],
        "aro": "S R3 G3 M1 P D1 N1 S",
        "ava": "S N1 D1 P M1 G3 R3 S"
    },
    "32. Ragavardhini": {
        "scale": [
            0,
            3,
            4,
            5,
            7,
            8,
            10
        ],
        "aro": "S R3 G3 M1 P D1 N2 S",
        "ava": "S N2 D1 P M1 G3 R3 S"
    },
    "33. Gangeyabhushani": {
        "scale": [
            0,
            3,
            4,
            5,
            7,
            8,
            11
        ],
        "aro": "S R3 G3 M1 P D1 N3 S",
        "ava": "S N3 D1 P M1 G3 R3 S"
    },
    "34. Vagadheeswari": {
        "scale": [
            0,
            3,
            4,
            5,
            7,
            9,
            10
        ],
        "aro": "S R3 G3 M1 P D2 N2 S",
        "ava": "S N2 D2 P M1 G3 R3 S"
    },
    "35. Shulini": {
        "scale": [
            0,
            3,
            4,
            5,
            7,
            9,
            11
        ],
        "aro": "S R3 G3 M1 P D2 N3 S",
        "ava": "S N3 D2 P M1 G3 R3 S"
    },
    "36. Chalanata": {
        "scale": [
            0,
            3,
            4,
            5,
            7,
            10,
            11
        ],
        "aro": "S R3 G3 M1 P D3 N3 S",
        "ava": "S N3 D3 P M1 G3 R3 S"
    },
    "37. Salagam": {
        "scale": [
            0,
            1,
            2,
            6,
            7,
            8,
            9
        ],
        "aro": "S R1 G1 M2 P D1 N1 S",
        "ava": "S N1 D1 P M2 G1 R1 S"
    },
    "38. Jalarnavam": {
        "scale": [
            0,
            1,
            2,
            6,
            7,
            8,
            10
        ],
        "aro": "S R1 G1 M2 P D1 N2 S",
        "ava": "S N2 D1 P M2 G1 R1 S"
    },
    "39. Jhalavarali": {
        "scale": [
            0,
            1,
            2,
            6,
            7,
            8,
            11
        ],
        "aro": "S R1 G1 M2 P D1 N3 S",
        "ava": "S N3 D1 P M2 G1 R1 S"
    },
    "40. Navaneetam": {
        "scale": [
            0,
            1,
            2,
            6,
            7,
            9,
            10
        ],
        "aro": "S R1 G1 M2 P D2 N2 S",
        "ava": "S N2 D2 P M2 G1 R1 S"
    },
    "41. Pavani": {
        "scale": [
            0,
            1,
            2,
            6,
            7,
            9,
            11
        ],
        "aro": "S R1 G1 M2 P D2 N3 S",
        "ava": "S N3 D2 P M2 G1 R1 S"
    },
    "42. Raghupriya": {
        "scale": [
            0,
            1,
            2,
            6,
            7,
            10,
            11
        ],
        "aro": "S R1 G1 M2 P D3 N3 S",
        "ava": "S N3 D3 P M2 G1 R1 S"
    },
    "43. Gavambodhi": {
        "scale": [
            0,
            1,
            3,
            6,
            7,
            8,
            9
        ],
        "aro": "S R1 G2 M2 P D1 N1 S",
        "ava": "S N1 D1 P M2 G2 R1 S"
    },
    "44. Bhavapriya": {
        "scale": [
            0,
            1,
            3,
            6,
            7,
            8,
            10
        ],
        "aro": "S R1 G2 M2 P D1 N2 S",
        "ava": "S N2 D1 P M2 G2 R1 S"
    },
    "45. Shubhapantuvarali": {
        "scale": [
            0,
            1,
            3,
            6,
            7,
            8,
            11
        ],
        "aro": "S R1 G2 M2 P D1 N3 S",
        "ava": "S N3 D1 P M2 G2 R1 S"
    },
    "46. Shadvidamargini": {
        "scale": [
            0,
            1,
            3,
            6,
            7,
            9,
            10
        ],
        "aro": "S R1 G2 M2 P D2 N2 S",
        "ava": "S N2 D2 P M2 G2 R1 S"
    },
    "47. Suvarnangi": {
        "scale": [
            0,
            1,
            3,
            6,
            7,
            9,
            11
        ],
        "aro": "S R1 G2 M2 P D2 N3 S",
        "ava": "S N3 D2 P M2 G2 R1 S"
    },
    "48. Divyamani": {
        "scale": [
            0,
            1,
            3,
            6,
            7,
            10,
            11
        ],
        "aro": "S R1 G2 M2 P D3 N3 S",
        "ava": "S N3 D3 P M2 G2 R1 S"
    },
    "49. Dhavalambari": {
        "scale": [
            0,
            1,
            4,
            6,
            7,
            8,
            9
        ],
        "aro": "S R1 G3 M2 P D1 N1 S",
        "ava": "S N1 D1 P M2 G3 R1 S"
    },
    "50. Namanarayani": {
        "scale": [
            0,
            1,
            4,
            6,
            7,
            8,
            10
        ],
        "aro": "S R1 G3 M2 P D1 N2 S",
        "ava": "S N2 D1 P M2 G3 R1 S"
    },
    "51. Kamavardhani": {
        "scale": [
            0,
            1,
            4,
            6,
            7,
            8,
            11
        ],
        "aro": "S R1 G3 M2 P D1 N3 S",
        "ava": "S N3 D1 P M2 G3 R1 S"
    },
    "52. Ramapriya": {
        "scale": [
            0,
            1,
            4,
            6,
            7,
            9,
            10
        ],
        "aro": "S R1 G3 M2 P D2 N2 S",
        "ava": "S N2 D2 P M2 G3 R1 S"
    },
    "53. Gamanashrama": {
        "scale": [
            0,
            1,
            4,
            6,
            7,
            9,
            11
        ],
        "aro": "S R1 G3 M2 P D2 N3 S",
        "ava": "S N3 D2 P M2 G3 R1 S"
    },
    "54. Vishwambari": {
        "scale": [
            0,
            1,
            4,
            6,
            7,
            10,
            11
        ],
        "aro": "S R1 G3 M2 P D3 N3 S",
        "ava": "S N3 D3 P M2 G3 R1 S"
    },
    "55. Syamalangi": {
        "scale": [
            0,
            2,
            3,
            6,
            7,
            8,
            9
        ],
        "aro": "S R2 G2 M2 P D1 N1 S",
        "ava": "S N1 D1 P M2 G2 R2 S"
    },
    "56. Shanmukhapriya": {
        "scale": [
            0,
            2,
            3,
            6,
            7,
            8,
            10
        ],
        "aro": "S R2 G2 M2 P D1 N2 S",
        "ava": "S N2 D1 P M2 G2 R2 S"
    },
    "57. Simhendramadhyamam": {
        "scale": [
            0,
            2,
            3,
            6,
            7,
            8,
            11
        ],
        "aro": "S R2 G2 M2 P D1 N3 S",
        "ava": "S N3 D1 P M2 G2 R2 S"
    },
    "58. Hemavati": {
        "scale": [
            0,
            2,
            3,
            6,
            7,
            9,
            10
        ],
        "aro": "S R2 G2 M2 P D2 N2 S",
        "ava": "S N2 D2 P M2 G2 R2 S"
    },
    "59. Dharmavati": {
        "scale": [
            0,
            2,
            3,
            6,
            7,
            9,
            11
        ],
        "aro": "S R2 G2 M2 P D2 N3 S",
        "ava": "S N3 D2 P M2 G2 R2 S"
    },
    "60. Neetimati": {
        "scale": [
            0,
            2,
            3,
            6,
            7,
            10,
            11
        ],
        "aro": "S R2 G2 M2 P D3 N3 S",
        "ava": "S N3 D3 P M2 G2 R2 S"
    },
    "61. Kantamani": {
        "scale": [
            0,
            2,
            4,
            6,
            7,
            8,
            9
        ],
        "aro": "S R2 G3 M2 P D1 N1 S",
        "ava": "S N1 D1 P M2 G3 R2 S"
    },
    "62. Rishabhapriya": {
        "scale": [
            0,
            2,
            4,
            6,
            7,
            8,
            10
        ],
        "aro": "S R2 G3 M2 P D1 N2 S",
        "ava": "S N2 D1 P M2 G3 R2 S"
    },
    "63. Latangi": {
        "scale": [
            0,
            2,
            4,
            6,
            7,
            8,
            11
        ],
        "aro": "S R2 G3 M2 P D1 N3 S",
        "ava": "S N3 D1 P M2 G3 R2 S"
    },
    "64. Vachaspati": {
        "scale": [
            0,
            2,
            4,
            6,
            7,
            9,
            10
        ],
        "aro": "S R2 G3 M2 P D2 N2 S",
        "ava": "S N2 D2 P M2 G3 R2 S"
    },
    "65. Mechakalyani": {
        "scale": [
            0,
            2,
            4,
            6,
            7,
            9,
            11
        ],
        "aro": "S R2 G3 M2 P D2 N3 S",
        "ava": "S N3 D2 P M2 G3 R2 S"
    },
    "66. Chitrambari": {
        "scale": [
            0,
            2,
            4,
            6,
            7,
            10,
            11
        ],
        "aro": "S R2 G3 M2 P D3 N3 S",
        "ava": "S N3 D3 P M2 G3 R2 S"
    },
    "67. Sucharitra": {
        "scale": [
            0,
            3,
            4,
            6,
            7,
            8,
            9
        ],
        "aro": "S R3 G3 M2 P D1 N1 S",
        "ava": "S N1 D1 P M2 G3 R3 S"
    },
    "68. Jyoti Swarupini": {
        "scale": [
            0,
            3,
            4,
            6,
            7,
            8,
            10
        ],
        "aro": "S R3 G3 M2 P D1 N2 S",
        "ava": "S N2 D1 P M2 G3 R3 S"
    },
    "69. Dhatuvardhani": {
        "scale": [
            0,
            3,
            4,
            6,
            7,
            8,
            11
        ],
        "aro": "S R3 G3 M2 P D1 N3 S",
        "ava": "S N3 D1 P M2 G3 R3 S"
    },
    "70. Nasikabhushani": {
        "scale": [
            0,
            3,
            4,
            6,
            7,
            9,
            10
        ],
        "aro": "S R3 G3 M2 P D2 N2 S",
        "ava": "S N2 D2 P M2 G3 R3 S"
    },
    "71. Kosalam": {
        "scale": [
            0,
            3,
            4,
            6,
            7,
            9,
            11
        ],
        "aro": "S R3 G3 M2 P D2 N3 S",
        "ava": "S N3 D2 P M2 G3 R3 S"
    },
    "72. Rasikapriya": {
        "scale": [
            0,
            3,
            4,
            6,
            7,
            10,
            11
        ],
        "aro": "S R3 G3 M2 P D3 N3 S",
        "ava": "S N3 D3 P M2 G3 R3 S"
    }
}

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
