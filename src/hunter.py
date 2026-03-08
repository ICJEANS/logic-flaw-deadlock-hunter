import re
from pathlib import Path


def analyze_text(text: str):
    issues = []
    lines = text.splitlines()
    for i, l in enumerate(lines, start=1):
        if re.search(r"while\s+True\s*:", l):
            issues.append(("high", "InfiniteLoop", i, "while True detected; ensure break/timeout"))
    acquires = [re.findall(r"(\w+)\.acquire\(\)", l) for l in lines]
    order = [a[0] for a in acquires if a]
    if len(order) >= 2 and len(set(order[:2])) == 2:
        issues.append(("medium", "Deadlock", 1, "Multiple lock acquire order detected; validate global lock ordering"))
    if re.search(r"threading\.Thread|asyncio\.create_task", text):
        issues.append(("low", "RaceCondition", 1, "Concurrency detected; validate shared-state synchronization"))
    return issues


def analyze_path(target: str):
    p = Path(target)
    files = [p] if p.is_file() else [f for f in p.rglob("*.py")]
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
