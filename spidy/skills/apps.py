"""Launch native applications on Windows / Mac / Linux."""
from __future__ import annotations
import os
import shutil
import subprocess
import sys


def open_app(exe: str) -> tuple[bool, str]:
    """Try to launch `exe`. Returns (ok, message)."""
    if not exe:
        return False, "No application specified."

    # Windows: `start` handles URIs & app aliases (calc, notepad, ms-settings:, ...)
    if sys.platform == "win32":
        try:
            subprocess.Popen(f'start "" {exe}', shell=True)
            return True, f"Opening {exe}."
        except Exception as e:
            return False, f"Couldn't launch {exe}: {e}"

    # POSIX
    if shutil.which(exe):
        try:
            subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"Opening {exe}."
        except Exception as e:
            return False, f"Couldn't launch {exe}: {e}"

    opener = "open" if sys.platform == "darwin" else "xdg-open"
    try:
        subprocess.Popen([opener, exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, f"Opening {exe}."
    except Exception as e:
        return False, f"I don't know how to open '{exe}'."
