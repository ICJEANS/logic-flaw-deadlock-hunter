import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))
import unittest
from tempfile import TemporaryDirectory
from hunter import analyze_text, analyze_path, to_report


class TestHunter(unittest.TestCase):
    def test_detect_infinite_loop(self):
        rows = analyze_text("while True:\n    pass\n")
        self.assertTrue(any(r[1] == "InfiniteLoop" for r in rows))

    def test_detect_while_one_infinite_loop(self):
        rows = analyze_text("while 1:\n    pass\n")
        self.assertTrue(any(r[1] == "InfiniteLoop" for r in rows))

    def test_ignore_commented_infinite_loop(self):
        rows = analyze_text("# while True:\npass\n")
        self.assertFalse(any(r[1] == "InfiniteLoop" for r in rows))

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

    def test_detect_lock_leak(self):
        rows = analyze_text("lock_a.acquire()\nprint('work')\n")
        self.assertTrue(any(r[1] == "LockLeak" for r in rows))

    def test_analyze_path_missing_target(self):
        self.assertEqual(analyze_path('/tmp/no-such-hunter-target-12345'), [])

    def test_analyze_path_includes_pyw(self):
        with TemporaryDirectory() as td:
            f = Path(td) / "x.pyw"
            f.write_text("while True:\n    pass\n")
            rows = analyze_path(td)
            self.assertTrue(any(r[1] == "InfiniteLoop" for r in rows))

    def test_race_condition_requires_shared_write_signal(self):
        rows = analyze_text("import threading\nthreading.Thread(target=lambda: None)\n")
        self.assertFalse(any(r[1] == "RaceCondition" for r in rows))

    def test_report_orders_severity(self):
        report = to_report([
            ("low", "RaceCondition", "f.py", 2, "x"),
            ("high", "InfiniteLoop", "f.py", 1, "y"),
        ])
        self.assertLess(report.find("|high|InfiniteLoop"), report.find("|low|RaceCondition"))

    def test_blank_line_breaks_lock_sequence(self):
        sample = (
            "lock_a.acquire()\n"
            "\n"
            "lock_b.acquire()\n"
        )
        rows = analyze_text(sample)
        self.assertFalse(any(r[1] == "Deadlock" for r in rows))

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
