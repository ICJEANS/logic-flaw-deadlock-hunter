import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))
import unittest
from hunter import analyze_text

class TestHunter(unittest.TestCase):
    def test_detect_infinite_loop(self):
        rows = analyze_text("while True:\n    pass\n")
        self.assertTrue(any(r[1] == "InfiniteLoop" for r in rows))

if __name__ == '__main__':
    unittest.main()
