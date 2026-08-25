"""Spidy main window - dark chat UI with sidebar, mic toggle, and status pill."""
from __future__ import annotations
import queue
import threading

import customtkinter as ctk

from config import APP_NAME, APP_TAGLINE, COLORS, WINDOW_MIN, WINDOW_SIZE
from core import permissions
from core.assistant import Assistant
from core.voice import Voice
from skills.reminders import ReminderChecker
from ui.widgets import ChatBubble, SidebarButton, StatusPill


ctk.set_appearance_mode("dark")


class SpidyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} · {APP_TAGLINE}")
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN)
        self.configure(fg_color=COLORS["bg"])

        self.assistant = Assistant(self)
        self.voice = Voice()
        self._ui_queue: "queue.Queue[tuple]" = queue.Queue()
        self._wake_on = False

        self._build_layout()
        self._start_workers()
        self.after(80, self._pump_ui_queue)

        # Boot message
        self._add_bot(
            f"Hi, I'm {APP_NAME} 🕷️  — your offline companion. "
            "Type below, click the mic, or turn on the wake word and just say “Hey Spidy”.\n"
            "Everything runs on this machine. I'll ask before touching anything sensitive."
        )
        self.voice.speak(f"Hello. I'm {APP_NAME}. Ready when you are.")

    # ------------------------------------------------------------------ #
    #                              LAYOUT                                #
    # ------------------------------------------------------------------ #

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ----- sidebar ----- #
        side = ctk.CTkFrame(self, width=220, fg_color=COLORS["panel"], corner_radius=0)
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)

        brand = ctk.CTkFrame(side, fg_color="transparent")
        brand.pack(pady=(20, 16), padx=18, anchor="w")
        ctk.CTkLabel(brand, text="🕷️", font=("Segoe UI Emoji", 26)).pack(side="left")
        ctk.CTkLabel(
            brand, text=APP_NAME, font=("Segoe UI Semibold", 22),
            text_color=COLORS["accent"],
        ).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            side, text="QUICK ACTIONS",
            font=("Segoe UI", 10, "bold"), text_color=COLORS["text_dim"],
        ).pack(anchor="w", padx=22, pady=(6, 6))

        actions = [
            ("Daily briefing",   "☀", lambda: self._quick("daily briefing")),
            ("Show reminders",   "⏰", lambda: self._quick("show reminders")),
            ("Show meetings",    "📅", lambda: self._quick("my meetings")),
            ("Show notes",       "📝", lambda: self._quick("show notes")),
            ("Screenshot",       "📸", lambda: self._quick("screenshot")),
            ("Tell me a joke",   "😄", lambda: self._quick("tell me a joke")),
            ("Activity log",     "🔐", lambda: self._quick("activity log")),
            ("Help",             "❔", lambda: self._quick("help")),
        ]
        for label, icon, cmd in actions:
            SidebarButton(side, label, cmd, icon).pack(fill="x", padx=12, pady=2)

        ctk.CTkFrame(side, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=18, pady=18)

        # Wake word toggle
        self._wake_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            side, text="Wake word: “Hey Spidy”",
            variable=self._wake_var,
            command=self._toggle_wake,
            progress_color=COLORS["accent"],
            text_color=COLORS["text"],
            font=("Segoe UI", 11),
        ).pack(anchor="w", padx=20, pady=6)

        # Privacy footer
        privacy = ctk.CTkFrame(side, fg_color=COLORS["panel_alt"], corner_radius=10)
        privacy.pack(side="bottom", fill="x", padx=12, pady=14)
        ctk.CTkLabel(
            privacy, text="🔒  Fully local",
            font=("Segoe UI Semibold", 11), text_color=COLORS["success"],
        ).pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(
            privacy,
            text="No cloud, no telemetry.\nI ask before every sensitive action.",
            font=("Segoe UI", 10), text_color=COLORS["text_dim"], justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 10))

        # ----- main pane ----- #
        main = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(main, fg_color=COLORS["panel"], corner_radius=0, height=54)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        ctk.CTkLabel(
            header, text=APP_TAGLINE,
            font=("Segoe UI", 12), text_color=COLORS["text_dim"],
        ).pack(side="left", padx=18)
        self.status = StatusPill(header)
        self.status.pack(side="right", padx=14)

        # Chat scroll area
        self.chat_area = ctk.CTkScrollableFrame(
            main, fg_color=COLORS["bg"], corner_radius=0,
            scrollbar_button_color=COLORS["panel_alt"],
            scrollbar_button_hover_color=COLORS["border"],
        )
        self.chat_area.grid(row=1, column=0, sticky="nsew", padx=14, pady=(10, 0))
        self.chat_area.grid_columnconfigure(0, weight=1)

        # Input bar
        bar = ctk.CTkFrame(main, fg_color=COLORS["panel"], corner_radius=0, height=76)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)

        self.mic_btn = ctk.CTkButton(
            bar, text="🎙", width=48, height=44, corner_radius=22,
            fg_color=COLORS["panel_alt"], hover_color=COLORS["border"],
            text_color=COLORS["accent"], font=("Segoe UI Emoji", 18),
            command=self._on_mic_click,
        )
        self.mic_btn.grid(row=0, column=0, padx=(14, 8), pady=16)

        self.entry = ctk.CTkEntry(
            bar, height=44, corner_radius=22,
            placeholder_text="Ask Spidy anything…  (Enter to send)",
            fg_color=COLORS["panel_alt"], border_color=COLORS["border"],
            text_color=COLORS["text"], placeholder_text_color=COLORS["text_dim"],
            font=("Segoe UI", 13),
        )
        self.entry.grid(row=0, column=1, sticky="ew", pady=16)
        self.entry.bind("<Return>", self._on_send)

        self.send_btn = ctk.CTkButton(
            bar, text="Send", width=90, height=44, corner_radius=22,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_dark"],
            text_color="white", font=("Segoe UI Semibold", 12),
            command=self._on_send,
        )
        self.send_btn.grid(row=0, column=2, padx=(8, 14), pady=16)

    # ------------------------------------------------------------------ #
    #                            EVENTS                                  #
    # ------------------------------------------------------------------ #

    def _on_send(self, _event=None):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self._add_user(text)
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _quick(self, text: str):
        self._add_user(text)
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _on_mic_click(self):
        if not self.voice.enabled_stt:
            self._add_bot("Speech recognition isn't available. Install `pyaudio` and `SpeechRecognition`.")
            return
        if not permissions.request(self, "mic", "Use microphone for a single voice command"):
            self._add_bot("Mic access denied.")
            return
        self.status.set("Listening…", "accent")
        self.mic_btn.configure(text="●", text_color=COLORS["danger"])
        threading.Thread(target=self._listen_once, daemon=True).start()

    def _listen_once(self):
        text = self.voice.listen_once(timeout=6)
        self._ui_queue.put(("mic_done",))
        if not text:
            self._ui_queue.put(("bot", "I didn't catch that."))
            return
        self._ui_queue.put(("user", text))
        reply = self.assistant.handle(text)
        if reply:
            self._ui_queue.put(("bot", reply))
            self.voice.speak(reply)

    def _toggle_wake(self):
        want = self._wake_var.get()
        if want and not self._wake_on:
            if not permissions.request(self, "mic", "Continuously listen for the wake word ‘Hey Spidy’"):
                self._wake_var.set(False)
                return
            self.voice.start_wake_listener(self._on_wake)
            self._wake_on = True
            self.status.set("Wake word ON · listening", "accent")
            self._add_bot("Wake word is on. Say “Hey Spidy” followed by your command.")
        elif not want and self._wake_on:
            self.voice.stop_wake_listener()
            self._wake_on = False
            self.status.set("Idle · fully local", "success")
            self._add_bot("Wake word turned off.")

    def _on_wake(self, payload: str):
        # payload is anything the user said AFTER "hey spidy"
        text = payload.strip()
        if not text:
            self._ui_queue.put(("bot", "Yes?"))
            self.voice.speak("Yes?")
            # brief follow-up capture
            follow = self.voice.listen_once(timeout=5)
            if not follow:
                return
            text = follow
        self._ui_queue.put(("user", text))
        reply = self.assistant.handle(text)
        if reply:
            self._ui_queue.put(("bot", reply))
            self.voice.speak(reply)

    def _process(self, text: str):
        self._ui_queue.put(("status", ("Thinking…", "warn")))
        reply = self.assistant.handle(text)
        self._ui_queue.put(("status", ("Idle · fully local", "success")))
        if reply:
            self._ui_queue.put(("bot", reply))
            self.voice.speak(reply)

    # ------------------------------------------------------------------ #
    #                       WORKERS & UI PUMP                            #
    # ------------------------------------------------------------------ #

    def _start_workers(self):
        self._reminder_thread = ReminderChecker(
            on_due=lambda r: self._ui_queue.put(("reminder", r)), interval=15
        )
        self._reminder_thread.start()

    def _pump_ui_queue(self):
        try:
            while True:
                kind, *rest = self._ui_queue.get_nowait()
                if kind == "bot":
                    self._add_bot(rest[0])
                elif kind == "user":
                    self._add_user(rest[0])
                elif kind == "status":
                    text, color = rest[0]
                    self.status.set(text, color)
                elif kind == "mic_done":
                    self.mic_btn.configure(text="🎙", text_color=COLORS["accent"])
                    self.status.set("Idle · fully local", "success")
                elif kind == "reminder":
                    r = rest[0]
                    msg = f"⏰ Reminder: {r.get('text', '(no text)')}"
                    self._add_bot(msg)
                    self.voice.speak(msg)
        except queue.Empty:
            pass
        self.after(80, self._pump_ui_queue)

    # ------------------------------------------------------------------ #
    #                          CHAT HELPERS                              #
    # ------------------------------------------------------------------ #

    def _add_bot(self, text: str):
        bubble = ChatBubble(self.chat_area, text, sender="bot")
        bubble.pack(fill="x", anchor="w")
        self.after(50, self._scroll_bottom)

    def _add_user(self, text: str):
        bubble = ChatBubble(self.chat_area, text, sender="user")
        bubble.pack(fill="x", anchor="e")
        self.after(50, self._scroll_bottom)

    def _scroll_bottom(self):
        try:
            self.chat_area._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    # ------------------------------------------------------------------ #

    def destroy(self):
        try:
            self.voice.stop_wake_listener()
            self._reminder_thread.stop()
        except Exception:
            pass
        super().destroy()
