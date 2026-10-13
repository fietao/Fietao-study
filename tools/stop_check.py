"""Stop hook: if this turn has a **Check question:** label but never touched
progress.md or scores.md, send Claude back to update them (once)."""
import json
import sys


def blocks(entry):
    c = entry.get("message", {}).get("content", [])
    return [{"type": "text", "text": c}] if isinstance(c, str) else c


def main():
    hook = json.load(sys.stdin)
    if hook.get("stop_hook_active"):
        return  # already sent back once; don't loop
    with open(hook["transcript_path"], encoding="utf-8") as f:
        entries = [json.loads(l) for l in f if l.strip()]

    # start of this turn = last real user message (not a tool result, not injected meta)
    start = 0
    for i, e in enumerate(entries):
        if e.get("type") == "user" and not e.get("isMeta") and \
                any(b.get("type") == "text" for b in blocks(e)):
            start = i
    turn = [e for e in entries[start + 1:] if e.get("type") == "assistant"]

    text = " ".join(b.get("text", "") for e in turn for b in blocks(e) if b.get("type") == "text")
    if "**Check question:**" not in text:
        return  # not a tutoring reply
    touched = json.dumps([b.get("input", {}) for e in turn for b in blocks(e)
                          if b.get("type") == "tool_use"])
    if "progress.md" in touched or "scores.md" in touched:
        return
    print(json.dumps({
        "decision": "block",
        "reason": "Study observer: this reply has a check question but progress.md/scores.md were not "
                  "updated. Log any graded answer in scores.md and update progress.md (per CLAUDE.md), "
                  "then repeat the lesson text last. If nothing was graded or learned this turn, say so in one line.",
    }))


if __name__ == "__main__":
    main()
