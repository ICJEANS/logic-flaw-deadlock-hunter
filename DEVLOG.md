# DEVLOG
- Implemented static checks for while-true infinite loop risks.
- Added lock-order/deadlock heuristic and concurrency race-condition hint.
- Added simulation report formatter with safe workaround guidance.
- Added unit test + GitHub Actions CI.

## 2026-03-08 Iteration 1
- Replaced naive deadlock heuristic with lock-order graphing based on acquire sequence pairs.
- Deadlock warning now triggers only when reversed acquisition order pairs are observed (A->B and B->A), reducing false positives.
- Added tests for both risky and safe lock-order scenarios:
  - `test_detect_reversed_lock_order_deadlock_risk`
  - `test_no_deadlock_for_single_lock_order`
- Local test evidence:
  - Command: `python3 -m unittest discover -s tests -v`
  - Result: `Ran 3 tests in 0.000s` / `OK`
