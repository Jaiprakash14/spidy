"""Shell command execution - always behind a permission popup."""
from __future__ import annotations
import subprocess


_BLOCKED = ("rm -rf", "format ", "del /f", "shutdown", "mkfs", ":(){:|:&};:")


def is_dangerous(cmd: str) -> bool:
    low = cmd.lower()
    return any(b in low for b in _BLOCKED)


def run(cmd: str, timeout: int = 15) -> tuple[bool, str]:
    if not cmd.strip():
        return False, "Empty command."
    if is_dangerous(cmd):
        return False, "That command looks destructive — I refuse to run it."
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        combined = out
        if err:
            combined += ("\n" if combined else "") + f"[stderr] {err}"
        if not combined:
            combined = f"(command exited with code {result.returncode})"
        # Trim big outputs
        if len(combined) > 2000:
            combined = combined[:2000] + "\n… (truncated)"
        return result.returncode == 0, combined
    except subprocess.TimeoutExpired:
        return False, "Command timed out."
    except Exception as e:
        return False, f"Error: {e}"
