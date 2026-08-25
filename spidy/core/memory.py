"""Local JSON-backed storage for reminders, notes, meetings.

Nothing here ever leaves the disk. All files live under /data.
"""
from __future__ import annotations
import json
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


_lock = threading.Lock()


def _load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save(path: Path, items: list[dict]) -> None:
    with _lock:
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(items, indent=2, default=str), encoding="utf-8")


class Store:
    """Tiny generic JSON list-store."""

    def __init__(self, path: Path):
        self.path = path

    def all(self) -> list[dict]:
        return _load(self.path)

    def add(self, **fields: Any) -> dict:
        items = self.all()
        item = {
            "id": uuid.uuid4().hex[:8],
            "created_at": datetime.now().isoformat(timespec="seconds"),
            **fields,
        }
        items.append(item)
        _save(self.path, items)
        return item

    def remove(self, item_id: str) -> bool:
        items = self.all()
        new = [x for x in items if x.get("id") != item_id]
        changed = len(new) != len(items)
        if changed:
            _save(self.path, new)
        return changed

    def clear(self) -> int:
        n = len(self.all())
        _save(self.path, [])
        return n

    def update(self, item_id: str, **fields: Any) -> bool:
        items = self.all()
        for it in items:
            if it.get("id") == item_id:
                it.update(fields)
                _save(self.path, items)
                return True
        return False
