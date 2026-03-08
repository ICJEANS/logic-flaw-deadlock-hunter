import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))
import unittest
from hunter import analyze_text


class TestHunter(unittest.TestCase):
    def test_detect_infinite_loop(self):
        rows = analyze_text("while True:\n    pass\n")
        self.assertTrue(any(r[1] == "InfiniteLoop" for r in rows))

    def test_detect_while_one_infinite_loop(self):
        rows = analyze_text("while 1:\n    pass\n")
        self.assertTrue(any(r[1] == "InfiniteLoop" for r in rows))

    def test_detect_reversed_lock_order_deadlock_risk(self):
        sample = (
            "lock_a.acquire()\n"
            "lock_b.acquire()\n"
            "lock_b.release()\n"
            "lock_a.release()\n"
            "lock_b.acquire()\n"
            "lock_a.acquire()\n"
        )
        rows = analyze_text(sample)
        self.assertTrue(any(r[1] == "Deadlock" for r in rows))

    def test_no_deadlock_for_single_lock_order(self):
        sample = (
            "lock_a.acquire()\n"
            "lock_b.acquire()\n"
            "lock_b.release()\n"
            "lock_a.release()\n"
            "lock_a.acquire()\n"
            "lock_b.acquire()\n"
        )
        rows = analyze_text(sample)
        self.assertFalse(any(r[1] == "Deadlock" for r in rows))


if __name__ == '__main__':
    unittest.main()
