---
name: flashcards
description: Drill a class's word cards (notes/VOCAB.md) one at a time in chat, grade each answer against the exact source wording, and log the result. Use when the user says "flashcards", "drill vocab", "quiz me on terms", or "cards for <class>".
---

# Flashcards

Cards come from `<class>/notes/VOCAB.md`. Each card is a **term** plus the exact quote and its source.
If the file has no cards yet, offer to make them from `notes/` or `materials/` first (quote word for word, with slide/page).

## Pick the cards
- Ask which class if it isn't clear. Default to 10 cards.
- Order: terms from mistake-log rows first, then terms never drilled, then the rest at random.
- If the user names a lecture or topic, use only that section.

## One card at a time
1. Ask confidence 1–3 (guess / unsure / sure) for this card.
2. Show the term only, labeled `**Card:**` (not `**Check question:**`; scores are logged once per round, so the
   Stop hook should not fire on every card). Never show the definition in the same message.
3. Wait for the user's answer.
4. Grade against the quote, not by feel:
   - **Got it**: every key idea in the quote is there (own words are fine).
   - **Partial**: some key ideas missing. Name the missing part in one line.
   - **Missed**: wrong or blank. Show the exact quote with its source.
5. If missed or partial, put the card back 3 cards later in this round.

## After the round
- Append one line to `<class>/scores.md`: today's date, the topic, the format, got/total, the average confidence
  (rounded), and `flashcards` as the source.
  - Format: use the checklist column that tests definitions (e.g. `Define`). If the class has none, ask which to use.
  - Topic: copy a checklist topic exactly. If cards spanned several topics, log one line per topic.
- Add one mistake-log row in `progress.md` per missed card (under 200 characters).
- Update the `progress.md` box per the shared rules (✅ only after 2 passing scores in a row).
- Finish with one line: score, and the 1–3 terms to redo next time.

Update the files first, then write the summary line last.
