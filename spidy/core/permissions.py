"""Permission system - every sensitive action goes through here.

Spidy NEVER performs a sensitive action (network, mic, shell, email, etc.)
without an explicit user approval. Every decision is written to an audit log.
"""
from __future__ import annotations
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk

from config import ACTIVITY_LOG, COLORS, SENSITIVE_ACTIONS, SETTINGS_FILE


_lock = threading.Lock()


def _log(action: str, detail: str, decision: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {decision:<7} | {action:<14} | {detail}\n"
    with _lock:
        ACTIVITY_LOG.parent.mkdir(exist_ok=True)
        with open(ACTIVITY_LOG, "a", encoding="utf-8") as f:
            f.write(line)


def _remembered(action: str) -> Optional[bool]:
    if not SETTINGS_FILE.exists():
        return None
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        return data.get("always_allow", {}).get(action)
    except Exception:
        return None


def _remember(action: str, allow: bool) -> None:
    data: dict = {}
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    data.setdefault("always_allow", {})[action] = allow
    SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


class PermissionDialog(ctk.CTkToplevel):
    """Modal popup asking the user to approve a sensitive action."""

    result: Optional[bool] = None
    remember: bool = False

    def __init__(self, parent, action: str, detail: str):
        super().__init__(parent)
        self.title("Spidy · Permission needed")
        self.geometry("460x260")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["panel"])
        self.transient(parent)
        self.grab_set()
        self.attributes("-topmost", True)

        title = SENSITIVE_ACTIONS.get(action, action)
        ctk.CTkLabel(
            self,
            text="🔒  Permission needed",
            font=("Segoe UI Semibold", 18),
            text_color=COLORS["accent"],
        ).pack(pady=(22, 6))

        ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 13),
            text_color=COLORS["text"],
            wraplength=400,
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            self,
            text=detail,
            font=("Consolas", 11),
            text_color=COLORS["text_dim"],
            wraplength=400,
            justify="left",
        ).pack(pady=(0, 12), padx=20)

        self._remember_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self,
            text="Always allow this action",
            variable=self._remember_var,
            text_color=COLORS["text_dim"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"],
        ).pack(pady=(0, 12))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=4)
        ctk.CTkButton(
            row, text="Deny", width=110, height=34,
            fg_color=COLORS["panel_alt"], hover_color=COLORS["border"],
            text_color=COLORS["text"], command=self._deny,
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            row, text="Allow", width=110, height=34,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_dark"],
            text_color="white", command=self._allow,
        ).pack(side="left", padx=6)

        self.protocol("WM_DELETE_WINDOW", self._deny)
        self.bind("<Return>", lambda _e: self._allow())
        self.bind("<Escape>", lambda _e: self._deny())

    def _allow(self):
        self.result = True
        self.remember = self._remember_var.get()
        self.destroy()

    def _deny(self):
        self.result = False
        self.remember = self._remember_var.get()
        self.destroy()


def request(parent, action: str, detail: str = "") -> bool:
    """Ask the user for permission. Blocks until they decide. Returns True/False."""
    saved = _remembered(action)
    if saved is True:
        _log(action, detail, "AUTO-OK")
        return True
    if saved is False:
        _log(action, detail, "AUTO-NO")
        return False

    dlg = PermissionDialog(parent, action, detail or SENSITIVE_ACTIONS.get(action, ""))
    parent.wait_window(dlg)
    granted = bool(dlg.result)
    if dlg.remember:
        _remember(action, granted)
    _log(action, detail, "ALLOW" if granted else "DENY")
    return granted


def log_action(action: str, detail: str = "") -> None:
    """Log a non-sensitive action (e.g. note added, reminder set)."""
    _log(action, detail, "INFO")


def read_activity(limit: int = 200) -> list[str]:
    if not ACTIVITY_LOG.exists():
        return []
    lines = ACTIVITY_LOG.read_text(encoding="utf-8").splitlines()
    return lines[-limit:]
