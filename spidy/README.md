# 🕷️ Spidy — your offline AI companion

Spidy is a **Windows desktop assistant** that lives entirely on your machine. No cloud, no telemetry, no data leaks. It talks, listens, remembers, and asks permission before doing anything sensitive.

![status](https://img.shields.io/badge/version-1.0.0-e63946)  ![offline](https://img.shields.io/badge/mode-fully%20offline-5fd39a)  ![python](https://img.shields.io/badge/python-3.10%2B-blue)

---

## ✨ What Spidy can do

| Category | Examples |
|---|---|
| **Voice + Text + Chat UI** | Type, click the mic, or turn on the “Hey Spidy” wake word |
| **Apps** | `open notepad`, `launch chrome`, `run vs code` |
| **Web** | `search python tutorials`, `open https://github.com` |
| **Notes** | `note that dinner is at 8`, `show notes`, `clear notes` |
| **Reminders** | `remind me to call mom in 10 min`, `show reminders` |
| **Meetings** | `schedule meeting with Alex tomorrow 10am`, `my meetings` |
| **Email drafts** | `email john@x.com about invoice` — opens your mail client, you review + send |
| **System** | `screenshot`, `volume up`, `volume down`, `mute` |
| **Shell** | `run dir`, `run ipconfig` (permission popup + destructive-command blocker) |
| **Info** | `time`, `date`, `joke`, `daily briefing` |
| **Privacy** | `activity log` — see every action Spidy took, with your approve/deny decisions |

---

## 🔒 Privacy guarantees (baked in)

1. **Nothing leaves your machine** unless you press Enter on a mailto: draft or approve a browser open.
2. **Every sensitive action shows a popup** — Allow / Deny, with an optional "Always allow".
3. **Everything is logged locally** to `data/activity.log` with a timestamp.
4. **Ollama is optional**. Without it, Spidy still runs — it just uses a lighter rule-based reply.
5. **No API keys, no accounts, no login.**

> ⚠️ **One honest caveat**: the speech-to-text step uses Google's free web API through the `SpeechRecognition` library, which means voice audio (only when you're actually speaking) briefly touches Google's servers. Everything else — TTS, chat, storage, actions — is 100% local. To go fully offline for STT too, swap `recognize_google` for `Vosk` in `core/voice.py` (a P1 item on the backlog).

---

## 🚀 Setup on Windows

### 1. Install prerequisites
- **Python 3.10+** → <https://python.org> (tick “Add Python to PATH” during install)
- **Ollama** (optional but recommended for smart chat) → <https://ollama.com>

After installing Ollama, open a terminal and pull a model:
```bat
ollama pull mistral
```

### 2. Get Spidy
Copy the whole `spidy` folder anywhere on your PC.

### 3. Run
Double-click **`run.bat`**.  
On first launch it will:
1. Create a virtual environment (`.venv/`)
2. Install all dependencies
3. Warn you if Ollama isn't running (Spidy still works)
4. Launch the chat window

That's it. Say “Hey Spidy” or start typing.

> 💡 Tip: If `pyaudio` fails to install, download the correct wheel from  
> <https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio> and `pip install <that-wheel>.whl`.

---

## 🕹️ Using the mic

- **Click 🎙** — record a single command
- **Toggle "Wake word"** in the sidebar — Spidy listens continuously for **"Hey Spidy …"**  
  (a mic permission popup shows the first time you enable it)

---

## 📁 Project layout

```
spidy/
├── run.bat                # one-click Windows launcher
├── requirements.txt
├── main.py                # entry point
├── config.py              # paths, colors, wake words, sensitive-action list
├── core/
│   ├── assistant.py       # orchestrates intents -> skills / Ollama
│   ├── brain.py           # intent parser + Ollama chat client
│   ├── voice.py           # pyttsx3 TTS + SR wake-word loop
│   ├── permissions.py     # permission popups + audit log
│   └── memory.py          # local JSON store
├── skills/
│   ├── apps.py            # launch apps
│   ├── web.py             # open URLs + search
│   ├── notes.py
│   ├── reminders.py       # includes background due-checker
│   ├── meetings.py
│   ├── email_skill.py     # mailto: draft only
│   ├── shell.py           # command runner with destructive-cmd blocker
│   ├── system.py          # screenshot + volume + mute
│   ├── briefing.py        # daily summary from LOCAL data
│   └── fun.py             # jokes, greetings
├── ui/
│   ├── app.py             # main window
│   └── widgets.py         # chat bubbles, sidebar buttons, status pill
└── data/                  # created at runtime
    ├── reminders.json
    ├── notes.json
    ├── meetings.json
    ├── settings.json      # remembered "always allow" choices
    └── activity.log       # audit trail
```

---

## 🛠️ Troubleshooting

| Issue | Fix |
|---|---|
| `pyaudio` install fails | Install a prebuilt wheel from the link above |
| Ollama not responding | Run `ollama serve` in another terminal, then `ollama pull mistral` |
| Mic doesn't work | Windows → Settings → Privacy → Microphone → allow desktop apps |
| Voice sounds robotic | It's pyttsx3 — fully offline. To change voice, edit `core/voice.py` and pick a different `voice.id` |
| Want a different Ollama model | Edit `OLLAMA_MODEL` in `config.py` (e.g. `llama3`, `phi3`) |

---

## 🕷️ Credits
Built with `customtkinter`, `pyttsx3`, `SpeechRecognition`, `python-dateutil`, `pycaw`, `pyautogui`.  
Everything else is Spidy's own — 100% local, 100% yours.
