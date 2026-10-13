import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from report import calibration, card  # noqa: E402
from status import summarize  # noqa: E402

PROGRESS = """# Progress

Next exam: 2099-01-01

## Coverage checklist (Define / Explain)

| Topic | Define | Explain |
|---|---|---|
| Cells | {mark} | ⬜ |

## Mistake log

| Topic | Notes |
|---|---|
| Cells | {note} |
"""

SCORES = """# Scores

## Log
| Date | Topic | Format | Score | Conf | Source |
|---|---|---|---|---|---|
{rows}
"""


def make_class(mark="⬜", rows="", note="short"):
    d = Path(tempfile.mkdtemp()) / "bio"
    d.mkdir()
    (d / "progress.md").write_text(PROGRESS.format(mark=mark, note=note), encoding="utf-8")
    (d / "scores.md").write_text(SCORES.format(rows=rows), encoding="utf-8")
    return d


def row(score, topic="Cells", fmt="Define", conf="2", day="2099-01-01"):
    return f"| {day} | {topic} | {fmt} | {score} | {conf} | quiz |"


class TestStatus(unittest.TestCase):
    def test_check_needs_two_passes_in_a_row(self):
        s = summarize(make_class("✅", "\n".join([row("5/5"), row("2/5")])))
        self.assertIn("UNEARNED ✅: Cells / Define needs 2 passing scores in a row", s["flags"])

    def test_two_passes_earn_check(self):
        s = summarize(make_class("✅", "\n".join([row("2/5"), row("4/5"), row("5/5")])))
        self.assertEqual(s["flags"], [])
        self.assertEqual(s["done"], 1)

    def test_typo_in_topic_is_flagged(self):
        s = summarize(make_class(rows=row("1/1", topic="Cell")))
        self.assertIn("UNKNOWN TOPIC in scores.md: 'Cell' (copy the checklist name exactly)", s["flags"])

    def test_typo_in_format_is_flagged(self):
        s = summarize(make_class(rows=row("1/1", fmt="Trace")))
        self.assertTrue(any(f.startswith("UNKNOWN FORMAT") for f in s["flags"]))

    def test_long_mistake_row_is_flagged(self):
        s = summarize(make_class(note="x" * 201))
        self.assertTrue(any(f.startswith("LONG MISTAKE ROW (201 chars)") for f in s["flags"]))


class TestReport(unittest.TestCase):
    def test_calibration_averages_by_confidence(self):
        rows = [r.strip("|").split("|") for r in [row("1/2", conf="3"), row("2/2", conf="3"), row("0/4", conf="1")]]
        rows = [[c.strip() for c in r] for r in rows]
        self.assertEqual(calibration(rows), {"3": (0.75, 2), "1": (0.0, 1)})

    def test_calibration_skips_missing_confidence(self):
        self.assertEqual(calibration([["2099-01-01", "Cells", "Define", "1/1", "-", "quiz"]]), {})

    def test_card_escapes_html(self):
        s = summarize(make_class(note="<script>"))
        self.assertIn("&lt;script&gt;", card(s))
        self.assertNotIn("<script>", card(s))


if __name__ == "__main__":
    unittest.main()
