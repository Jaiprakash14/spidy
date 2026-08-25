"""Spidy assistant orchestrator - routes intents to skills, chats via Ollama."""
from __future__ import annotations
from datetime import datetime
from typing import Callable

from core import brain, permissions
from skills import apps, briefing, email_skill, fun, meetings, notes, reminders, shell, system, web


HELP_TEXT = """Here's what I can do (voice or text):
• Open apps      — "open notepad", "launch chrome"
• Web            — "search python tutorials", "open https://github.com"
• Notes          — "note that dinner is at 8", "show notes"
• Reminders      — "remind me to call mom in 10 min", "show reminders"
• Meetings       — "schedule meeting with Alex tomorrow 10am", "my meetings"
• Email drafts   — "email john@x.com about invoice"
• System         — "screenshot", "volume up/down", "mute"
• Shell          — "run dir", "run ipconfig"
• Info           — "time", "date", "weather", "joke", "daily briefing"
• Privacy        — "activity log" to see every action I've taken
Say "Hey Spidy" then your command — or just type below."""


class Assistant:
    """Stateless-ish command handler; keeps a short chat history for Ollama."""

    def __init__(self, parent_window):
        self.parent = parent_window
        self.history: list[dict] = []

    # main entry
    def handle(self, text: str) -> str:
        if not text:
            return ""
        intent = brain.parse(text)
        return self._dispatch(intent)

    def _dispatch(self, intent) -> str:
        name = intent.name
        args = intent.args

        if name == "noop":
            return ""
        if name == "help":
            return HELP_TEXT
        if name == "greeting":
            return fun.greeting()
        if name == "thanks":
            return fun.thanks()
        if name == "goodbye":
            return fun.goodbye()
        if name == "joke":
            return fun.joke()
        if name == "time":
            return f"It's {datetime.now().strftime('%H:%M')}."
        if name == "date":
            return f"Today is {datetime.now().strftime('%A, %d %B %Y')}."
        if name == "briefing":
            return briefing.briefing()
        if name == "activity_log":
            log = permissions.read_activity(30)
            return "Recent activity (local only):\n" + ("\n".join(log[-15:]) or "(nothing yet)")

        # ---------- sensitive actions ---------- #
        if name == "open_app":
            exe = args.get("exe") or args.get("app", "")
            if not permissions.request(self.parent, "open_app", f"Launch: {exe}"):
                return "OK, I won't open that."
            ok, msg = apps.open_app(exe)
            return msg

        if name == "open_url":
            url = args.get("url", "")
            if not permissions.request(self.parent, "open_browser", f"Open URL: {url}"):
                return "OK, browser stays closed."
            ok, msg = web.open_url(url)
            return msg

        if name == "web_search":
            q = args.get("q", "")
            if not permissions.request(self.parent, "web_search", f"Search: {q}"):
                return "Search cancelled."
            ok, msg = web.search(q)
            return msg

        if name == "email":
            who = args.get("who", "").strip()
            subj = args.get("subject", "")
            if not permissions.request(self.parent, "email", f"Draft email to {who}"):
                return "Email cancelled."
            ok, msg = email_skill.draft(who, subject=subj)
            return msg

        if name == "shell":
            cmd = args.get("cmd", "")
            if not permissions.request(self.parent, "shell", f"Run: {cmd}"):
                return "Command cancelled."
            ok, out = shell.run(cmd)
            return out

        if name == "screenshot":
            if not permissions.request(self.parent, "screenshot", "Capture the current screen"):
                return "Screenshot cancelled."
            ok, msg = system.screenshot()
            return msg

        # ---------- local-only actions ---------- #
        if name == "add_reminder":
            return reminders.add(args.get("what", ""), args.get("when"))
        if name == "list_reminders":
            return reminders.list_all()
        if name == "clear_reminders":
            return reminders.clear()

        if name == "add_note":
            return notes.add(args.get("text", ""))
        if name == "list_notes":
            return notes.list_all()
        if name == "clear_notes":
            return notes.clear()

        if name == "schedule_meeting":
            return meetings.add(args.get("who"), args.get("when"))
        if name == "list_meetings":
            return meetings.list_all()

        if name == "volume_up":
            ok, msg = system.volume_change(+0.1)
            return msg
        if name == "volume_down":
            ok, msg = system.volume_change(-0.1)
            return msg
        if name == "mute":
            ok, msg = system.mute()
            return msg

        if name == "weather":
            city = args.get("city", "your city")
            return (f"I stay fully offline, so I can't fetch live weather for {city}. "
                    "Say 'search weather in <city>' and I'll open it in your browser instead.")

        # ---------- open-ended chat via Ollama ---------- #
        if name == "chat":
            user_text = args.get("text", intent.raw)
            reply = brain.chat(user_text, self.history)
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": reply})
            return reply

        return "I didn't quite get that. Say 'help' to see what I can do."
