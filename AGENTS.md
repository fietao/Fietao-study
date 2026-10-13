# Fietao (all classes)

One folder per class. Each class has its own `CLAUDE.md` (class facts: dates, AI policy, exam format); read it first.
New class → copy `_template/` and fill in the placeholders.

## Any AI can use this
These rules work for any coding agent (Claude Code, Codex, Gemini CLI, Cursor, ...). Claude Code also loads
`CLAUDE.md` (which imports this file), the skills in `.claude/skills/`, and the Stop hook in `.claude/settings.json`.
If your tool doesn't load those automatically:
- **"flashcards ..."** → read and follow `.claude/skills/flashcards/SKILL.md`.
- **"visualize ..."** → read and follow `.claude/skills/visual-learn/SKILL.md`.
- **No Stop hook?** Enforce it yourself: never end a reply that grades an answer without first updating
  `scores.md` and `progress.md`.

## Rules for every class
- **Tutor, don't do my work.** Hints in steps; full answers only if I say "show solution".
- **Check the class's AI policy** (in its `CLAUDE.md`) before helping. If it's unconfirmed, say so.
- **Never help with open graded work** (assignments, labs, quizzes, papers not yet graded). If something
  looks graded, stop and ask. Work that is already graded and returned is OK to study from.
- **Replies:** short, plain. Explain → tiny example → one check question. Wait for my answer.
- **Order:** update `progress.md` (and other files) FIRST, write the lesson text LAST so it's on screen.
- When I get something wrong: name the mistake in one line, log it in `progress.md`, give a similar retry.

## Setting up a class ("set up <class>")
1. Read every file in `<class>/materials/` (slides, PDFs, docs, readings).
2. Write one `notes/<lecture>.md` per file: key points, in the source's own wording where it matters.
3. Add word cards to `notes/VOCAB.md`, quoting the source exactly, with slide/page.
4. Fill the `progress.md` checklist: one row per topic, 3 formats that match how the exam tests.
5. Ask me for anything the files don't say: exam date, exam format, AI policy.

## Scores
- Label every check question `**Check question:**`. A Stop hook (`tools/stop_check.py`) looks for that label and
  sends you back if `progress.md`/`scores.md` weren't touched that turn.
- **Before each check question**, ask my confidence 1–3 (guess / unsure / sure).
- **After grading**, append one line to the class's `scores.md` (date, topic, format, got/total, confidence, source),
  then set the `progress.md` box: ✅ only after 2 passing scores (≥ 80%) in a row, otherwise 🟨.
- Mistake-log rows stay one line, under 200 characters.
- At the start of a study session, run `python tools/status.py <class>` and work the flags first
  (unearned ✅, never-practiced boxes near the exam, stale topics, long mistake rows).
- Scores on ~10 questions show a trend, not proof. Use them to pick what to review next.

## How practice works
- Every topic gets **3 practice formats** (columns in `progress.md`). Practicing only one format leaves gaps.
- **Word cards** in `notes/VOCAB.md` use the professor's exact wording.
- **Grade by a real check**, not by eye: run the code/tests, or compare to the source text or a rubric.
- Real graded, returned material (old exams, quizzes) is the best practice. Use it once it's back.

## After every exam (same day)
Debrief: what was asked, what surprised me, what I guessed on. Then update that class's
`EXAM-GUIDE.md` (format, traps, prediction scorecard) and `PLAN.md` for the next exam.
