"""Daily briefing - a summary of today, built entirely from LOCAL data."""
from __future__ import annotations
from datetime import datetime

from skills import notes, reminders, meetings


def briefing() -> str:
    now = datetime.now()
    greet = "morning" if now.hour < 12 else "afternoon" if now.hour < 18 else "evening"
    lines = [
        f"Good {greet}. It's {now.strftime('%A, %d %B %Y — %H:%M')}.",
    ]

    rs = reminders.all_items()
    if rs:
        lines.append(f"You have {len(rs)} reminder(s):")
        for r in rs[:5]:
            due = r.get("due") or "anytime"
            lines.append(f"  • {r['text']} — {due}")
    else:
        lines.append("No reminders on the board.")

    ms = meetings.all_items()
    if ms:
        lines.append(f"{len(ms)} meeting(s) scheduled:")
        for m in ms[:5]:
            when = m.get("when") or "no time set"
            who = m.get("who") or "someone"
            lines.append(f"  • {who} — {when}")

    ns = notes.all_items()
    if ns:
        lines.append(f"And {len(ns)} note(s) saved.")

    lines.append("Ready when you are.")
    return "\n".join(lines)
