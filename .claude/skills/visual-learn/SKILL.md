---
name: visual-learn
description: Create an interactive visual lesson (one HTML page) for one topic. Use when the user says "visualize", "show me", "draw this", or "help me see how X works". Works for any subject, not only code.
---

# Visual Learn

Turn one topic into one short interactive HTML lesson. Match the user's language and never mix two languages on one page.
Base it on the class's `notes/` and `materials/` when they cover the topic, so the page uses the professor's wording.

## 1. Pick the picture

Match the topic's shape to its main interaction:

| Topic shape | Page shape |
|---|---|
| Process | Step-by-step flow with a Play button |
| System or parts | Clickable map with a side panel |
| Compare | Table |
| History | Timeline |
| Cause and effect | Slider simulator |
| Quantities | Chart |

Use the simplest shape that fits. If two fit, pick the one the user can play with (a slider beats a chart;
a step flow beats a static map). If the topic has several ideas, teach the one that matters most.

## 2. Build the lesson

One self-contained HTML file: inline CSS, JavaScript, and SVG. No external files except Google Fonts.

The page must:
- **Ask a "guess first" question** before anything is revealed. Keep Play/Next/slider locked until the user
  picks a guess, then say whether the guess was right. Keep the lock in the JavaScript, not only in the HTML:
  a redraw function that runs on page load (e.g. `render()` setting `next.disabled = step >= last`) will
  silently unlock the buttons. Gate on a `guessed` flag.
- **Start on step 1** (or the slider at 0), not the full picture. Parts not reached yet stay faint with their words hidden.
- **Reveal parts one at a time** through the chosen interaction.
- **End with a check question** that has separate Hint and Answer buttons.
- **Keep the answer out of** the title, the intro, and figure captions. Name the topic or ask the question instead.
- Use short, plain words.

Style:
- Color tokens on `:root`, a dark version under `@media (prefers-color-scheme: dark)`, and an explicit `body` background.
- Works at phone width: no `min-width` over 400px; SVGs use `width: 100%` and a `viewBox`.
- Visible keyboard focus, readable contrast, and `prefers-reduced-motion` support (the final state must make sense without animation).

## Save and open

Save to `<class>/visuals/<topic-kebab>.html` (or `visuals/` at the repo root if no class applies), then open it in the browser.
Don't publish or upload the page without the user's permission.

## Before delivery, check
- One language only.
- The guess comes before the answer: trace the code path that runs on load and confirm Next/Play/slider are
  still disabled before any guess.
- Parts are revealed one at a time.
- Hint and Answer buttons both work.
- Light, dark, and phone-width layouts work.
- The file opens locally with no missing assets.
