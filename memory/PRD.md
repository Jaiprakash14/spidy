# Spidy — Offline AI Desktop Companion (Windows)

## Original problem statement
Build a Windows desktop AI assistant named **Spidy** with:
- Chat-style dark UI + voice + text
- Offline AI brain (Ollama)
- Everything: reminders, meetings, emails, apps, web, shell, briefing
- Privacy-first: permission popups before touching any user data
- Clean architecture, one-click launcher

## User choices (from ask_human)
- OS: Windows
- Voice engine: pyttsx3 (fully offline)
- Email: draft-only via mailto:
- Delivery: `/app/spidy/` folder + `spidy.zip`
- Wake word: always-listening "Hey Spidy"
- AI model: default (mistral)

## Architecture
```
spidy/
├── run.bat, main.py, config.py, requirements.txt, README.md
├── core/     assistant.py, brain.py, voice.py, permissions.py, memory.py
├── skills/   apps, web, notes, reminders, meetings, email_skill, shell, system, briefing, fun
├── ui/       app.py (CustomTkinter dark chat window), widgets.py
└── data/     JSON stores + activity.log (created at runtime)
```

## Implemented (v1.0.0 — 25 Aug 2026)
- Dark CustomTkinter chat UI, sidebar with 8 quick actions, status pill, mic button, wake-word toggle
- Voice: pyttsx3 TTS + SpeechRecognition STT + always-listening "Hey Spidy" loop
- Offline AI: Ollama chat client (`mistral` default) + graceful rule-based fallback
- Rule intent parser: 25+ patterns for apps, web, notes, reminders, meetings, email, shell, system, info
- Reminders with natural-language time parsing + background due-checker thread
- Meetings + notes local JSON stores
- Email via `mailto:` (opens user's mail client, they review + send)
- Shell command runner with destructive-command blocklist
- Screenshot, volume up/down, mute (pycaw)
- Daily briefing built from LOCAL data
- Permissions system with popup, "always allow" memory, tamper-visible `activity.log`
- One-click `run.bat` (venv setup + dep install + Ollama check + launch)
- Lint clean, parser smoke-tested

## Backlog (P1)
- Wake-word improvement: swap `speech_recognition.recognize_google` for fully-offline Vosk model (currently uses Google's free API for STT — the only cloud dependency; TTS is 100% local)
- Encrypted SMTP so Spidy can also *send* emails, not just draft
- Calendar file (.ics) import/export
- System tray icon + hotkey to summon window
- Ollama model picker in Settings panel
- Vosk / Whisper.cpp integration for offline STT (removes last cloud dep)

## Delivery
- Full folder: `/app/spidy/`
- ZIP: `/app/spidy.zip` (~30 KB, no venv)
