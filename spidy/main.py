"""Spidy - entry point."""
import sys
import traceback

from ui.app import SpidyApp


def main() -> int:
    try:
        app = SpidyApp()
        app.mainloop()
        return 0
    except Exception:
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return 1


if __name__ == "__main__":
    sys.exit(main())
