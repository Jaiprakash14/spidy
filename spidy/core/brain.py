"""Spidy brain - intent router + Ollama fallback.

Flow:
  1. Fast rule-based intent parser handles known commands (open X, remind me, etc.)
  2. If nothing matches, forward the text to Ollama for a natural reply
  3. If Ollama isn't running, use a light canned fallback so Spidy never freezes
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional

import requests

from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT


# ------------------------------ Intent shape ------------------------------ #

@dataclass
class Intent:
    name: str                          # e.g. "open_app", "add_reminder", "chat"
    args: dict[str, Any] = field(default_factory=dict)
    raw: str = ""

    def __repr__(self) -> str:
        return f"Intent({self.name}, {self.args})"


# ------------------------------ Rule parser ------------------------------- #

_APP_ALIASES = {
    "notepad": "notepad", "note pad": "notepad",
    "calculator": "calc", "calc": "calc",
    "paint": "mspaint", "ms paint": "mspaint",
    "explorer": "explorer", "file explorer": "explorer", "files": "explorer",
    "cmd": "cmd", "command prompt": "cmd", "terminal": "cmd",
    "powershell": "powershell",
    "chrome": "chrome", "google chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge", "microsoft edge": "msedge",
    "vs code": "code", "vscode": "code", "code": "code",
    "spotify": "spotify",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "settings": "ms-settings:",
}

_INTENT_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("greeting",        re.compile(r"^(hi|hello|hey|yo|good\s?(morning|afternoon|evening))\b", re.I)),
    ("thanks",          re.compile(r"\b(thanks|thank you|thx|appreciate)\b", re.I)),
    ("goodbye",         re.compile(r"\b(bye|goodbye|see ya|see you|good night)\b", re.I)),
    ("time",            re.compile(r"\b(what.?s (the )?time|current time|time now|what time is it)\b", re.I)),
    ("date",            re.compile(r"\b(what.?s (the|today.?s) date|today.?s date|date today|what day is it|what day)\b", re.I)),
    ("weather",         re.compile(r"\b(weather|temperature|forecast)(\s+in\s+(?P<city>[a-z ,]+))?", re.I)),
    ("joke",            re.compile(r"\b(joke|make me laugh|funny)\b", re.I)),
    ("briefing",        re.compile(r"\b(daily briefing|briefing|catch me up|what.?s (up|new))\b", re.I)),
    ("screenshot",      re.compile(r"\b(screenshot|screen shot|capture (my )?screen)\b", re.I)),
    ("volume_up",       re.compile(r"\b(volume up|increase volume|louder)\b", re.I)),
    ("volume_down",     re.compile(r"\b(volume down|decrease volume|quieter|lower volume)\b", re.I)),
    ("mute",            re.compile(r"\b(mute|silence)\b", re.I)),
    ("shell",           re.compile(r"^(run|exec|execute|shell)\s+(?P<cmd>.+)$", re.I)),
    ("open_app",        re.compile(r"^(open|launch|start)\s+(?P<app>.+)$", re.I)),
    ("web_search",      re.compile(r"^(search|google|look\s?up|find)\s+(for\s+)?(?P<q>.+)$", re.I)),
    ("open_url",        re.compile(r"^(open|go to|visit|browse)\s+(?P<url>(https?://|www\.)\S+)$", re.I)),
    ("add_reminder",    re.compile(r"^remind\s+me\s+(to\s+)?(?P<what>.+?)(\s+(at|in|on|tomorrow|today)\s+(?P<when>.+))?$", re.I)),
    ("list_reminders",  re.compile(r"\b((show|list|my)\s+reminders|what.?s\s+on\s+my\s+list)\b", re.I)),
    ("clear_reminders", re.compile(r"\b(clear|delete|remove)\s+(all\s+)?reminders?\b", re.I)),
    ("add_note",        re.compile(r"^(take a note|note that|note down|remember that|write down)\s+(?P<text>.+)$", re.I)),
    ("list_notes",      re.compile(r"\b((show|list|read|my)\s+notes)\b", re.I)),
    ("clear_notes",     re.compile(r"\b(clear|delete)\s+(all\s+)?notes?\b", re.I)),
    ("schedule_meeting",re.compile(r"^(schedule|book|set up)\s+(a\s+)?meeting(\s+with\s+(?P<who>[a-z ]+?))?(\s+(at|on|tomorrow|today)\s+(?P<when>.+))?$", re.I)),
    ("list_meetings",   re.compile(r"\b(my\s+)?(meetings|schedule|calendar)\b", re.I)),
    ("email",           re.compile(r"^(email|send (a|an) email|mail)\s+(?P<who>[\w.@ ]+?)(\s+about\s+(?P<subject>.+))?$", re.I)),
    ("activity_log",    re.compile(r"\b(activity log|audit log|what have you done|permission log)\b", re.I)),
    ("help",            re.compile(r"^(help|what can you do|commands)$", re.I)),
]


def _match_app(text: str) -> Optional[str]:
    t = text.lower().strip()
    if t in _APP_ALIASES:
        return _APP_ALIASES[t]
    for alias, exe in _APP_ALIASES.items():
        if alias in t:
            return exe
    return None


def parse(text: str) -> Intent:
    text = text.strip()
    if not text:
        return Intent("noop", raw=text)

    for name, pat in _INTENT_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        args: dict[str, Any] = {k: v.strip() for k, v in (m.groupdict() or {}).items() if v}
        if name == "open_app" and "app" in args:
            args["exe"] = _match_app(args["app"]) or args["app"].split()[0].lower()
        return Intent(name, args, raw=text)

    return Intent("chat", {"text": text}, raw=text)


# ------------------------------ Ollama chat ------------------------------- #

SYSTEM_PROMPT = (
    "You are Spidy, a friendly, concise offline desktop assistant. "
    "Keep replies short (1-3 sentences). Never claim to perform actions you "
    "were not asked to. If unsure, ask a clarifying question."
)


def _ollama_available() -> bool:
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False


def chat(user_text: str, history: Optional[list[dict]] = None, model: str = OLLAMA_MODEL) -> str:
    """Send user_text to Ollama; return assistant text or a graceful fallback."""
    if not _ollama_available():
        return _fallback_reply(user_text)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history[-8:])
    messages.append({"role": "user", "content": user_text})

    try:
        r = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=OLLAMA_TIMEOUT,
        )
        if r.status_code == 200:
            data = r.json()
            return (data.get("message") or {}).get("content", "").strip() or _fallback_reply(user_text)
    except Exception:
        pass
    return _fallback_reply(user_text)


_FALLBACKS = [
    "I'm running fully offline right now without Ollama, so I can't have a deep chat — try installing Ollama and running `ollama pull mistral`.",
    "My conversational brain isn't loaded. But I can still open apps, take notes, set reminders, and more.",
    "I couldn't reach Ollama, so I'll stay light. Say 'help' to see what I can do right now.",
]


def _fallback_reply(text: str) -> str:
    import random
    return random.choice(_FALLBACKS)
