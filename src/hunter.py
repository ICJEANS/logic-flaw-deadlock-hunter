import re
from pathlib import Path


ACQUIRE_RE = re.compile(r"(\w+)\.acquire\(\)")


def _lock_orders(lines: list[str]) -> set[tuple[str, str]]:
    orders: set[tuple[str, str]] = set()
    current: list[str] = []

    for line in lines:
        acquired = ACQUIRE_RE.findall(line)
        if acquired:
            current.extend(acquired)
            if len(current) >= 2:
                for i in range(len(current) - 1):
                    orders.add((current[i], current[i + 1]))
        if ".release(" in line:
            current = []

    return orders


def analyze_text(text: str):
    issues = []
    lines = text.splitlines()
    for i, l in enumerate(lines, start=1):
        check = l.split('#', 1)[0]
        if re.search(r"while\s+(True|1)\s*:", check):
            issues.append(("high", "InfiniteLoop", i, "while True/1 detected; ensure break/timeout"))

    orders = _lock_orders(lines)
    has_reversed_pair = any((b, a) in orders for a, b in orders if a != b)
    if has_reversed_pair:
        issues.append(("medium", "Deadlock", 1, "Inconsistent lock acquisition order detected across code paths"))

    acquires = len(re.findall(r"\.acquire\(\)", text))
    releases = len(re.findall(r"\.release\(\)", text))
    if acquires > releases:
        issues.append(("medium", "LockLeak", 1, "More lock acquire() than release() calls"))

    if re.search(r"threading\.Thread|asyncio\.create_task", text):
        issues.append(("low", "RaceCondition", 1, "Concurrency detected; validate shared-state synchronization"))
    return issues


def analyze_path(target: str):
    p = Path(target)
    if not p.exists():
        return []
    files = [p] if p.is_file() else sorted([f for f in p.rglob("*") if f.suffix in {'.py', '.pyw'}], key=lambda x: str(x))
    report = []
    for f in files:
        text = f.read_text(encoding='utf-8', errors='ignore')
        for sev, cat, line, msg in analyze_text(text):
            report.append((sev, cat, str(f), line, msg))
    return report


def to_report(rows):
    if not rows:
        return "No major logic/deadlock risks detected."
    s = ["# Simulation Report", "", "|Severity|Category|File|Line|Scenario|", "|---|---|---|---:|---|"]
    for r in rows:
        s.append(f"|{r[0]}|{r[1]}|{r[2]}|{r[3]}|{r[4]}|")
    s.append("\nSafe workaround: enforce lock ordering and add bounded timeout/retry.")
    return "\n".join(s)
