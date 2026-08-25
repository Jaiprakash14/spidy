"""Reminders - stored locally, checked by a background thread."""
from __future__ import annotations
import re
import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Optional

from dateutil import parser as dateparser

from core.memory import Store
from config import REMINDERS_FILE

_store = Store(REMINDERS_FILE)


# -------------------- natural-language time parsing ------------------- #

_REL_RE = re.compile(
    r"in\s+(?P<n>\d+)\s*(?P<unit>seconds?|secs?|minutes?|mins?|hours?|hrs?|days?)",
    re.I,
)


def parse_when(text: Optional[str]) -> Optional[datetime]:
    """Parse '10 min', 'tomorrow 5pm', 'at 18:00' -> datetime. None if unclear."""
    if not text:
        return None
    text = text.strip()
    now = datetime.now()

    m = _REL_RE.search(text)
    if m:
        n = int(m.group("n"))
        unit = m.group("unit").lower()
        if unit.startswith(("sec",)):
            return now + timedelta(seconds=n)
        if unit.startswith(("min",)):
            return now + timedelta(minutes=n)
        if unit.startswith(("hour", "hr")):
            return now + timedelta(hours=n)
        if unit.startswith("day"):
            return now + timedelta(days=n)

    lowered = text.lower()
    base = now
    if "tomorrow" in lowered:
        base = now + timedelta(days=1)
        text = re.sub(r"tomorrow", "", text, flags=re.I).strip()
    elif "today" in lowered:
        text = re.sub(r"today", "", text, flags=re.I).strip()

    text = re.sub(r"^(at|on)\s+", "", text, flags=re.I).strip()
    if not text:
        return base.replace(hour=9, minute=0, second=0, microsecond=0)

    try:
        dt = dateparser.parse(text, default=base.replace(second=0, microsecond=0), fuzzy=True)
        if dt < now:
            dt += timedelta(days=1)
        return dt
    except Exception:
        return None


# -------------------- CRUD ------------------------------------------- #

def add(text: str, when_text: Optional[str]) -> str:
    when = parse_when(when_text) if when_text else None
    item = _store.add(text=text, due=when.isoformat(timespec="minutes") if when else None, notified=False)
    if when:
        return f"OK, I'll remind you to “{text}” at {when.strftime('%a %d %b, %H:%M')}."
    return f"Reminder saved: “{text}” (no specific time — say ‘show reminders’ to review)."


def list_all() -> str:
    items = sorted(_store.all(), key=lambda x: x.get("due") or "9")
    if not items:
        return "No reminders — you're all clear."
    lines = []
    for i, r in enumerate(items, 1):
        due = r.get("due") or "anytime"
        lines.append(f"{i}. {r['text']}  ·  {due}")
    return "Your reminders:\n" + "\n".join(lines)


def clear() -> str:
    n = _store.clear()
    return f"Cleared {n} reminder(s)." if n else "Nothing to clear."


def all_items():
    return _store.all()


# -------------------- background checker ----------------------------- #

class ReminderChecker(threading.Thread):
    """Fires `on_due(reminder_dict)` when a reminder's due-time passes."""

    def __init__(self, on_due: Callable[[dict], None], interval: int = 20):
        super().__init__(daemon=True)
        self.on_due = on_due
        self.interval = interval
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        while not self._stop.is_set():
            try:
                now = datetime.now()
                for r in _store.all():
                    if r.get("notified") or not r.get("due"):
                        continue
                    try:
                        due = datetime.fromisoformat(r["due"])
                    except Exception:
                        continue
                    if due <= now:
                        _store.update(r["id"], notified=True)
                        self.on_due(r)
            except Exception:
                pass
            self._stop.wait(self.interval)
