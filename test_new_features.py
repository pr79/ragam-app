
import unittest
from src.music_theory import format_swara_sequence, note_to_swaras
from src.utils import save_uploaded_file, get_output_path

class TestNewFeatures(unittest.TestCase):
    def test_format_swara_sequence(self):
        # C is 0. C Major scale: 0, 2, 4, 5, 7, 9, 11
        # Tonic C=60
        # Notes: C, D, E
        events = [
            (0.0, 1.0, 60), # S
            (1.0, 2.0, 62), # R2
            (2.0, 3.0, 64)  # G3
        ]
        result = format_swara_sequence(events, 0)
        self.assertEqual(result, "S R2 G3")
        print(f"Swara Test: {result} [PASS]")

    def test_utils_import(self):
        # Just checking if function exists
        self.assertTrue(callable(save_uploaded_file))
        self.assertTrue(callable(get_output_path))
        print("Utils Import: [PASS]")

if __name__ == '__main__':
    unittest.main()
