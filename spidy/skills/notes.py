"""Notes - local, plaintext, private."""
from __future__ import annotations
from core.memory import Store
from config import NOTES_FILE

_store = Store(NOTES_FILE)


def add(text: str) -> str:
    if not text:
        return "What should I note down?"
    _store.add(text=text)
    return f"Noted: “{text}”"


def list_all() -> str:
    items = _store.all()
    if not items:
        return "You have no notes yet."
    lines = [f"{i+1}. {n['text']}" for i, n in enumerate(items)]
    return "Your notes:\n" + "\n".join(lines)


def clear() -> str:
    n = _store.clear()
    return f"Cleared {n} note(s)." if n else "There was nothing to clear."


def all_items():
    return _store.all()
