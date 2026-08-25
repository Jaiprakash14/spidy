"""Email skill - draft-only. Spidy opens the default mail client with a
pre-filled mailto: link so YOU review + send. Nothing is transmitted here.
"""
from __future__ import annotations
import urllib.parse
import webbrowser
from typing import Optional


def draft(to: str, subject: Optional[str] = None, body: Optional[str] = None) -> tuple[bool, str]:
    if not to:
        return False, "Who should I email?"
    params = {}
    if subject:
        params["subject"] = subject
    if body:
        params["body"] = body
    query = ("?" + urllib.parse.urlencode(params)) if params else ""
    url = f"mailto:{to.strip()}{query}"
    try:
        webbrowser.open(url, new=1)
        return True, f"Opened a draft email to {to}. Review it and hit send."
    except Exception as e:
        return False, f"Couldn't open mail client: {e}"
