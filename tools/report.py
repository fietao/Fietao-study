"""Build report.html: one card per class with the checklist, flags, mistakes, and confidence vs. score.

Usage: python tools/report.py      (then open report.html)
"""
import html
import sys
from pathlib import Path

from status import PASS, ROOT, summarize

OUT = ROOT / "report.html"
MARK = {"✅": "done", "🟨": "tried", "⬜": "todo", "—": "na"}
CONF = {"1": "Guess", "2": "Unsure", "3": "Sure"}


def calibration(rows):
    """Conf level -> (average score, number of tries). Rows without a 1-3 confidence are skipped."""
    out = {}
    for r in rows:
        if r[4] in CONF:
            got, total = (float(x) for x in r[3].split("/"))
            out.setdefault(r[4], []).append(got / total)
    return {c: (sum(v) / len(v), len(v)) for c, v in out.items()}


def card(s):
    e = html.escape
    head = "".join(f"<th>{e(f)}</th>" for f in s["formats"])
    body = "".join(
        f"<tr><td>{e(topic)}</td>" + "".join(f'<td class="{MARK.get(m, "na")}">{m}</td>' for m in row.values()) + "</tr>"
        for topic, row in s["checklist"].items())
    cal = calibration(s["rows"])
    bars = "".join(
        f'<div class="bar"><span>{CONF[c]}</span><div class="track"><i style="width:{avg * 100:.0f}%" '
        f'class="{"ok" if avg >= PASS else "low"}"></i></div><b>{avg:.0%} · {n} tries</b></div>'
        for c, (avg, n) in sorted(cal.items())) or "<p>No confidence ratings yet.</p>"
    flags = "".join(f"<li>{e(f)}</li>" for f in s["flags"]) or "<li>No flags</li>"
    mistakes = "".join(f"<li><b>{e(r[0])}</b> {e(r[1])}</li>" for r in s["mistakes"][:5] if len(r) > 1 and r[1])
    exam = f'{s["exam"]} · {s["days"]} days' if s["exam"] else "no exam date"
    return f"""<section>
<h2>{e(s["name"])}</h2><p class="sub">Next exam {exam} · ✅ {s["done"]}/{s["boxes"]} · 🟨 {s["tried"]} · ⬜ {s["left"]}
 · {s["attempts"]} graded tries ({s["week"]} this week)</p>
<table><tr><th>Topic</th>{head}</tr>{body}</table>
<h3>Confidence vs. score</h3><div class="cal">{bars}</div>
<h3>Flags</h3><ul>{flags}</ul>
<h3>Recent mistakes</h3><ul>{mistakes or "<li>None logged</li>"}</ul>
</section>"""


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Fietao</title><style>
:root{--bg:#f7f7f5;--card:#fff;--ink:#1d1d1f;--mute:#6b6b70;--line:#e3e3e0;--done:#d6f2dc;--tried:#fbefc8;
--todo:#f1f1ee;--ok:#3a9d5d;--low:#d9822b}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--card:#1e1e21;--ink:#ececef;--mute:#9a9aa1;--line:#2e2e33;
--done:#1f3d29;--tried:#3d3517;--todo:#26262a;--ok:#5cc282;--low:#e7a050}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif}
main{max-width:760px;margin:0 auto;padding:32px 16px}
h1{margin:0 0 4px}h2{margin:0}h3{margin:24px 0 8px;font-size:14px;text-transform:uppercase;color:var(--mute)}
.sub,main>p{color:var(--mute);margin:4px 0 16px}
section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;margin:16px 0}
table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid var(--line);text-align:left}
td:not(:first-child),th:not(:first-child){text-align:center;width:16%}
.done{background:var(--done)}.tried{background:var(--tried)}.todo{background:var(--todo)}
.bar{display:grid;grid-template-columns:70px 1fr 120px;gap:8px;align-items:center;margin:6px 0}
.bar i{display:block;height:10px;border-radius:5px}
.track{background:var(--todo);border-radius:5px}.bar .ok{background:var(--ok)}.bar .low{background:var(--low)}
.bar b{font-weight:500;color:var(--mute);font-size:13px}ul{margin:0;padding-left:20px}
</style></head><body><main><h1>Fietao</h1>
<p>✅ = 2 passing scores (≥ 80%) in a row · 🟨 tried · ⬜ not practiced. Confidence is rated before each answer.</p>
{cards}</main></body></html>"""


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    classes = [p for p in sorted(ROOT.iterdir())
               if p.is_dir() and not p.name.startswith("_") and (p / "scores.md").exists()]
    OUT.write_text(PAGE.replace("{cards}", "".join(card(summarize(c)) for c in classes)), encoding="utf-8")
    print(f"Wrote {OUT}")
