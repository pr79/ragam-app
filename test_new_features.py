
import unittest
import numpy as np
import soundfile as sf
import os
from pathlib import Path
from src.music_theory import format_swara_sequence, note_to_swaras
from src.utils import save_uploaded_file, get_output_path
from src.audio_processor import extract_flute_and_wind, extract_indian_percussion, split_guitars

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_workspace")
        self.test_dir.mkdir(exist_ok=True)
        
        # Create synthetic audio
        sr = 22050
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration))
        
        # 1. Sine wave (Harmonic) + Noise (Percussive)
        self.other_audio = np.sin(2 * np.pi * 440 * t) + np.random.normal(0, 0.1, len(t))
        self.other_path = self.test_dir / "other.wav"
        sf.write(self.other_path, self.other_audio, sr)
        
        # 2. Noise (Percussive)
        self.drums_audio = np.random.normal(0, 0.5, len(t))
        self.drums_path = self.test_dir / "drums.wav"
        sf.write(self.drums_path, self.drums_audio, sr)
        
        # 3. Stereo Guitar (L/R diff)
        self.guitar_audio = np.vstack([np.sin(2 * np.pi * 330 * t), np.cos(2 * np.pi * 330 * t)])
        self.guitar_path = self.test_dir / "guitar.wav"
        sf.write(self.guitar_path, self.guitar_audio.T, sr)

    def tearDown(self):
        if self.test_dir.exists():
            for f in self.test_dir.iterdir():
                f.unlink()
            self.test_dir.rmdir()

    def test_extract_flute_and_wind(self):
        out_path = self.test_dir / "flute.wav"
        res = extract_flute_and_wind(self.other_path, out_path)
        self.assertTrue(Path(res).exists())
        self.assertTrue(Path(res).stat().st_size > 0)

    def test_extract_indian_percussion(self):
        out_path = self.test_dir / "perc.wav"
        res = extract_indian_percussion(self.other_path, self.drums_path, out_path)
        self.assertTrue(Path(res).exists())
        self.assertTrue(Path(res).stat().st_size > 0)
        
    def test_split_guitars(self):
        lead_path = self.test_dir / "lead.wav"
        acoustic_path = self.test_dir / "acoustic.wav"
        l, r = split_guitars(self.guitar_path, lead_path, acoustic_path)
        self.assertTrue(Path(l).exists())
        self.assertTrue(Path(r).exists())

    def test_format_swara_sequence(self):
        # C is 0. C Major scale: 0, 2, 4, 5, 7, 9, 11
        # Tonic C=60
        events = [
            (0.0, 1.0, 60), # S
            (1.0, 2.0, 62), # R2
            (2.0, 3.0, 64)  # G3
        ]
        result = format_swara_sequence(events, 0)
        self.assertEqual(result, "S R2 G3")

if __name__ == '__main__':
    unittest.main()
