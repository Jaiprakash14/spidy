"""Spidy configuration - all settings in one place."""
from pathlib import Path

APP_NAME = "Spidy"
APP_TAGLINE = "Your offline AI companion"
VERSION = "1.0.0"

# --- Paths ---
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

REMINDERS_FILE = DATA_DIR / "reminders.json"
NOTES_FILE = DATA_DIR / "notes.json"
MEETINGS_FILE = DATA_DIR / "meetings.json"
ACTIVITY_LOG = DATA_DIR / "activity.log"
SETTINGS_FILE = DATA_DIR / "settings.json"

# --- Ollama (offline AI brain) ---
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "mistral"          # can be changed in Settings
OLLAMA_TIMEOUT = 30                # seconds

# --- Voice ---
WAKE_WORDS = ("hey spidy", "spidy", "hi spidy", "ok spidy")
TTS_RATE = 175                     # words / minute
TTS_VOLUME = 0.95
MIC_PHRASE_TIMEOUT = 6             # seconds of silence to end a command
MIC_LISTEN_TIMEOUT = 4             # seconds waiting for wake word each cycle

# --- UI ---
WINDOW_SIZE = "980x680"
WINDOW_MIN = (820, 560)

# Dark theme (Spidy palette — crimson accent on charcoal)
COLORS = {
    "bg":            "#0e0f13",
    "panel":         "#161821",
    "panel_alt":     "#1d2030",
    "border":        "#262a3d",
    "text":          "#e8eaf2",
    "text_dim":      "#8b90a8",
    "accent":        "#e63946",     # spider red
    "accent_dark":   "#a4222c",
    "user_bubble":   "#2a2f4a",
    "bot_bubble":    "#1a1c28",
    "success":       "#5fd39a",
    "warn":          "#f5c26b",
    "danger":        "#ff5a5f",
}

# Sensitive actions -> require permission popup
SENSITIVE_ACTIONS = {
    "open_browser":   "Open a web browser and load a URL",
    "web_search":     "Search the internet via your browser",
    "shell":          "Run a shell command on your machine",
    "email":          "Open your email client with a pre-filled draft",
    "mic":            "Access the microphone for voice input",
    "screenshot":     "Capture a screenshot of your desktop",
    "open_app":       "Launch an application on your system",
    "read_file":      "Read a file from your disk",
}
