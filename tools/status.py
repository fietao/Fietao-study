"""Study observer: flags gaps in each class folder that has a scores.md.

Usage: python tools/status.py            (all classes)
       python tools/status.py demo-bio101   (one class)
"""
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PASS = 0.8          # score fraction that counts as passing
STALE_DAYS = 5      # practiced topic not scored for this long = stale
EXAM_WINDOW = 7     # days before exam when ⬜ boxes get flagged
LONG_ROW = 200      # mistake-log row length limit


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def table_after(lines, heading_prefix):
    """Rows (as cell lists) of the first table after a heading, header row first."""
    start = next((i for i, l in enumerate(lines) if l.startswith(heading_prefix)), None)
    if start is None:
        return []
    rows = []
    for l in lines[start + 1:]:
        if l.startswith("|"):
            if not set(l) <= set("|-: "):
                rows.append(cells(l))
        elif rows:
            break
    return rows


def summarize(cls):
    """Parse one class folder. Returns summary numbers, flags, and the parsed tables."""
    progress = (cls / "progress.md").read_text(encoding="utf-8").splitlines()
    scores = (cls / "scores.md").read_text(encoding="utf-8").splitlines()
    today = date.today()
    out = []

    m = next((re.search(r"Next exam:\s*(\d{4}-\d{2}-\d{2})", l) for l in progress if "Next exam:" in l), None)
    exam = date.fromisoformat(m.group(1)) if m else None
    days = (exam - today).days if exam else None

    head = next(l for l in progress if l.startswith("## Coverage checklist"))
    formats = [f.strip() for f in re.search(r"\((.*)\)", head).group(1).split("/")]
    table = table_after(progress, "## Coverage checklist")
    cols = {f: table[0].index(f) for f in formats}
    checklist = {r[0]: {f: r[i] for f, i in cols.items()} for r in table[1:]}

    log = {}  # (topic, format) -> list of (date, fraction)
    rows = table_after(scores, "## Log")[1:]
    for r in rows:
        d, topic, fmt, score = r[0], r[1], r[2], r[3]
        if topic not in checklist:
            out.append(f"UNKNOWN TOPIC in scores.md: '{topic}' (copy the checklist name exactly)")
            continue
        if fmt not in formats:
            out.append(f"UNKNOWN FORMAT in scores.md: '{fmt}' (use {', '.join(formats)})")
            continue
        got, total = (float(x) for x in score.split("/"))
        log.setdefault((topic, fmt), []).append((date.fromisoformat(d), got / total))

    for topic, row in checklist.items():
        never = []
        for fmt, mark in row.items():
            hist = sorted(log.get((topic, fmt), []))
            if mark == "✅" and not (len(hist) >= 2 and all(s >= PASS for _, s in hist[-2:])):
                out.append(f"UNEARNED ✅: {topic} / {fmt} needs 2 passing scores in a row")
            if mark == "⬜" and days is not None and 0 <= days <= EXAM_WINDOW:
                never.append(fmt)
            if hist and (today - hist[-1][0]).days > STALE_DAYS and mark != "✅":
                out.append(f"STALE ({(today - hist[-1][0]).days}d): {topic} / {fmt}")
        if never:
            out.append(f"NEVER PRACTICED, exam in {days}d: {topic} — {', '.join(never)}")

    mistakes = table_after(progress, "## Mistake log")[1:]
    for r in mistakes:
        if len(r) > 1 and len(r[1]) > LONG_ROW:
            out.append(f"LONG MISTAKE ROW ({len(r[1])} chars): {r[0]} — split into one line per mistake")

    done = sum(m == "✅" for row in checklist.values() for m in row.values())
    boxes = sum(m != "—" for row in checklist.values() for m in row.values())
    tried = sum(m == "🟨" for row in checklist.values() for m in row.values())
    attempts = sum(len(h) for h in log.values())
    week = sum(1 for h in log.values() for d, _ in h if (today - d).days < 7)
    return {"name": cls.name, "exam": exam, "days": days, "done": done, "boxes": boxes, "tried": tried,
            "left": boxes - done - tried, "attempts": attempts, "week": week, "flags": out,
            "formats": formats, "checklist": checklist, "log": log, "rows": rows, "mistakes": mistakes,
            "progress": progress}


def check(cls):
    s = summarize(cls)
    exam, days, done, boxes, tried, out = s["exam"], s["days"], s["done"], s["boxes"], s["tried"], s["flags"]
    attempts, week = s["attempts"], s["week"]
    print(f"== {cls.name}: exam {exam or '?'} ({days if days is not None else '?'}d) · ✅ {done}/{boxes} boxes"
          f" · 🟨 {tried} started · ⬜ {boxes - done - tried} left · {attempts} graded tries ({week} this week)")
    print("\n".join(out) if out else "no flags")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console defaults to cp1252
    names = sys.argv[1:] or [p.name for p in sorted(ROOT.iterdir())
                             if p.is_dir() and not p.name.startswith("_") and (p / "scores.md").exists()]
    for n in names:
        check(ROOT / n)
