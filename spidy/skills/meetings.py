"""Meetings - lightweight calendar stored locally."""
from __future__ import annotations
from typing import Optional

from core.memory import Store
from config import MEETINGS_FILE
from skills.reminders import parse_when

_store = Store(MEETINGS_FILE)


def add(who: Optional[str], when_text: Optional[str], subject: Optional[str] = None) -> str:
    when = parse_when(when_text) if when_text else None
    label = who or "someone"
    _store.add(
        who=who or "",
        subject=subject or "",
        when=when.isoformat(timespec="minutes") if when else "",
    )
    if when:
        return f"Meeting with {label} scheduled for {when.strftime('%a %d %b, %H:%M')}."
    return f"Meeting with {label} saved (no time set — say ‘show meetings’)."


def list_all() -> str:
    items = sorted(_store.all(), key=lambda x: x.get("when") or "9")
    if not items:
        return "Your calendar is empty."
    lines = []
    for i, m in enumerate(items, 1):
        who = m.get("who") or "someone"
        when = m.get("when") or "no time set"
        lines.append(f"{i}. {who}  ·  {when}")
    return "Upcoming meetings:\n" + "\n".join(lines)


def all_items():
    return _store.all()
