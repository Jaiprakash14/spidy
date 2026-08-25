
 🕷️ Spidy — Your Offline AI Companion

Spidy is a **Windows desktop AI assistant** that lives entirely on your machine.  
No cloud. No telemetry. No data leaks. It talks, listens, remembers, controls your browser, and **asks permission before doing anything sensitive.**

![status](https://img.shields.io/badge/version-1.1.0-e63946)
![offline](https://img.shields.io/badge/mode-fully%20local-5fd39a)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![platform](https://img.shields.io/badge/platform-Windows-0078d4)

---

## ✨ Features

| Category | Examples |
|---|---|
| **Voice + Text + Chat UI** | Type, click the mic, or say **"Hey Spidy"** (wake word) |
| **Native apps** | `open notepad`, `launch chrome`, `open vs code` |
| **Web (default browser)** | `search python tutorials`, `open https://github.com` |
| **Browser automation** 🕸️ | `browse to gmail.com`, `play lofi on youtube`, `scroll down`, `click Login`, `type hello`, `press enter`, `screenshot the page`, `summarize this page`, `close browser` |
| **Notes** | `note that dinner is at 8`, `show notes`, `clear notes` |
| **Reminders** | `remind me to call mom in 10 min`, `show reminders` |
| **Meetings** | `schedule meeting with Alex tomorrow 10am`, `my meetings` |
| **Email drafts** | `email john@x.com about invoice` — opens mail client for review |
| **System** | `screenshot`, `volume up`, `volume down`, `mute` |
| **Shell** | `run dir`, `run ipconfig` (permission popup + destructive-cmd blocker) |
| **Info** | `time`, `date`, `joke`, `daily briefing` |
| **Privacy** | `activity log` — see every action Spidy took with your approve/deny |

---

## 🔒 Privacy Guarantees

1. **Nothing leaves your machine** unless you approve a browser open or a mailto: draft.
2. **Every sensitive action shows a popup** — Allow / Deny, with "Always allow" memory.
3. **Everything is logged locally** to `data/activity.log` with a timestamp.
4. **Ollama is optional.** Without it, Spidy falls back to a rule-based reply engine.
5. **No API keys. No accounts. No login.**

> ⚠️ **One honest caveat**: speech-to-text uses Google's free web API (via the `SpeechRecognition` library), so voice audio briefly touches Google servers *only when you speak*. TTS, chat, storage, and actions are 100% local. Swap `recognize_google` → Vosk in `core/voice.py` to go fully offline (P1 backlog).

---

## 🚀 Quick Start (Windows)

### 1. Prerequisites
- **Python 3.10+** — [python.org/downloads](https://python.org/downloads) *(tick "Add Python to PATH" during install)*
- **Ollama** *(optional, for smart chat)* — [ollama.com](https://ollama.com)
  ```bat
  ollama pull mistral
  ```

### 2. Clone & Run
```bat
git clone https://github.com/YOUR-USERNAME/spidy.git
cd spidy
run.bat
```

That's it. `run.bat` auto-creates a virtualenv, installs deps, downloads Chromium for browser automation (~150 MB, one time), and launches Spidy.

---

## 🎙️ Using Voice

- **Click the 🎙 button** — record a single command
- **Toggle "Wake word" in the sidebar** — Spidy listens continuously for **"Hey Spidy …"**  
  *(mic permission popup shows the first time)*

---

## 🕹️ Command Cheatsheet

```
hello                                       # greet
tell me a joke
what time is it
daily briefing

remind me to stretch in 10 min
show reminders
note that my wifi is spidy-net
show notes
schedule meeting with alex tomorrow 10am
my meetings

open notepad                                # native app (permission)
open https://github.com                     # default browser
search best coffee near me                  # web search

browse to gmail.com                         # Spidy's own Chromium
play lofi on youtube                        # searches + auto-plays
click Login                                 # click any button/link by text
type my.email@example.com
press tab
type mypassword
press enter
scroll down
summarize this page                         # Ollama-powered summary
screenshot the page
close browser

run dir                                     # shell (permission + safety blocker)
volume up  /  volume down  /  mute
screenshot                                  # desktop screenshot
activity log                                # audit trail
help
```

---

## 📁 Project Structure

```
spidy/
├── run.bat                  # one-click launcher
├── main.py                  # entry point
├── config.py                # paths, theme, wake words, sensitive actions
├── requirements.txt
├── README.md
├── core/
│   ├── assistant.py         # intent → skill dispatcher
│   ├── brain.py             # rule parser + Ollama client
│   ├── voice.py             # TTS + STT + wake-word loop
│   ├── permissions.py       # permission popups + audit log
│   └── memory.py            # local JSON store
├── skills/
│   ├── apps.py              # launch native apps
│   ├── web.py               # default-browser URL & search
│   ├── browser.py           # Playwright-controlled Chromium 🕸️
│   ├── notes.py
│   ├── reminders.py         # with background due-checker
│   ├── meetings.py
│   ├── email_skill.py       # mailto: drafts
│   ├── shell.py             # with destructive-cmd blocker
│   ├── system.py            # screenshot / volume / mute
│   ├── briefing.py          # local-data summary
│   └── fun.py
├── ui/
│   ├── app.py               # dark CustomTkinter chat window
│   └── widgets.py           # bubbles, sidebar, status pill
└── data/                    # created at runtime
    ├── reminders.json
    ├── notes.json
    ├── meetings.json
    ├── settings.json        # remembered "always allow"
    ├── activity.log         # audit trail
    └── browser_profile/     # Spidy's browser session
```

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `'python' is not recognized` | Reinstall Python and tick **"Add Python to PATH"** |
| `pyaudio` install fails | Install a prebuilt wheel from [gohlke wheels](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) → `pip install <file>.whl` |
| Ollama not detected | Run `ollama serve` in another terminal, then `ollama pull mistral` |
| Mic doesn't work | Windows → Settings → Privacy → Microphone → allow desktop apps |
| Voice sounds robotic | It's `pyttsx3` (100% offline). Edit `core/voice.py` to pick a different `voice.id` |
| Change Ollama model | Edit `OLLAMA_MODEL` in `config.py` — try `llama3`, `phi3`, etc. |
| Browser won't launch | `pip install playwright` and `playwright install chromium` inside `.venv` |

---

## 🗺️ Roadmap

- [ ] **Fully offline STT** — swap `recognize_google` → Vosk
- [ ] **System tray icon** + global hotkey
- [ ] **Real email send** via encrypted local SMTP
- [ ] **Settings panel** — model picker, voice picker, permission review
- [ ] **Plugin folder** — drop `.py` files into `plugins/` for auto-discovered commands
- [ ] **Vector memory** — Spidy remembers past conversations locally

---

## 🤝 Contributing

Spidy is a personal-companion project — PRs welcome for:
- New skills (drop into `skills/` + register an intent in `core/brain.py`)
- Better wake-word detection
- Vosk / Whisper.cpp integration for offline STT

---

## 📜 License

MIT — do whatever, just keep it local. 🕷️

Everything else is Spidy's own — 100% local, 100% yours. 🕷️
