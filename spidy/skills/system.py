"""System skills - screenshot, volume, mute. Cross-platform where possible."""
from __future__ import annotations
import sys
from datetime import datetime
from pathlib import Path

from config import DATA_DIR


def screenshot() -> tuple[bool, str]:
    try:
        import pyautogui
    except Exception as e:
        return False, f"pyautogui isn't available: {e}"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = DATA_DIR / f"screenshot_{ts}.png"
    try:
        img = pyautogui.screenshot()
        img.save(path)
        return True, f"Screenshot saved to {path}"
    except Exception as e:
        return False, f"Couldn't take screenshot: {e}"


# ---------------- Volume (Windows via pycaw) --------------------- #

def _win_volume():
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


def volume_change(delta: float) -> tuple[bool, str]:
    """delta in [-1.0 .. 1.0]. Positive = louder."""
    if sys.platform != "win32":
        return False, "Volume control only supported on Windows for now."
    try:
        vol = _win_volume()
        current = vol.GetMasterVolumeLevelScalar()
        new = max(0.0, min(1.0, current + delta))
        vol.SetMasterVolumeLevelScalar(new, None)
        return True, f"Volume set to {int(new * 100)}%."
    except Exception as e:
        return False, f"Couldn't change volume: {e}"


def mute() -> tuple[bool, str]:
    if sys.platform != "win32":
        return False, "Mute only supported on Windows for now."
    try:
        vol = _win_volume()
        vol.SetMute(not vol.GetMute(), None)
        return True, "Toggled mute."
    except Exception as e:
        return False, f"Couldn't toggle mute: {e}"
