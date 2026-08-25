"""Voice engine - pyttsx3 TTS + speech_recognition STT + wake-word listener.

Everything here is fully offline. The wake-word listener runs in its own
thread and calls `on_wake(text)` whenever the user says "Hey Spidy ..." or
similar. It grabs the microphone ONLY after permission has been granted.
"""
from __future__ import annotations
import threading
import time
from typing import Callable, Optional

try:
    import pyttsx3
except Exception:  # pragma: no cover
    pyttsx3 = None

try:
    import speech_recognition as sr
except Exception:  # pragma: no cover
    sr = None

from config import MIC_LISTEN_TIMEOUT, MIC_PHRASE_TIMEOUT, TTS_RATE, TTS_VOLUME, WAKE_WORDS


class Voice:
    def __init__(self):
        self.enabled_tts = pyttsx3 is not None
        self.enabled_stt = sr is not None
        self._engine = None
        self._tts_lock = threading.Lock()
        self._speaking = False
        if self.enabled_tts:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", TTS_RATE)
            self._engine.setProperty("volume", TTS_VOLUME)
            # Prefer a female-sounding voice if available (nicer for Spidy)
            for v in self._engine.getProperty("voices"):
                if "zira" in v.name.lower() or "female" in v.name.lower():
                    self._engine.setProperty("voice", v.id)
                    break

        self._recognizer = sr.Recognizer() if self.enabled_stt else None
        if self._recognizer:
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.pause_threshold = 0.8

        self._listener_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        self._paused = threading.Event()

    # -------------------------- TTS ------------------------------------ #

    def speak(self, text: str) -> None:
        if not (self.enabled_tts and text):
            return

        def _run():
            with self._tts_lock:
                self._speaking = True
                try:
                    self._engine.say(text)
                    self._engine.runAndWait()
                except RuntimeError:
                    # pyttsx3 event loop already running - reinitialise
                    try:
                        self._engine.stop()
                        self._engine.say(text)
                        self._engine.runAndWait()
                    except Exception:
                        pass
                finally:
                    self._speaking = False

        threading.Thread(target=_run, daemon=True).start()

    def stop_speaking(self) -> None:
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass

    # -------------------------- STT (single-shot) ---------------------- #

    def listen_once(self, timeout: float = 5.0, phrase_limit: float = MIC_PHRASE_TIMEOUT) -> Optional[str]:
        if not self.enabled_stt:
            return None
        try:
            with sr.Microphone() as mic:
                self._recognizer.adjust_for_ambient_noise(mic, duration=0.3)
                audio = self._recognizer.listen(mic, timeout=timeout, phrase_time_limit=phrase_limit)
            return self._recognizer.recognize_google(audio).strip()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception:
            # e.g. offline google recognizer fails - try sphinx
            try:
                return self._recognizer.recognize_sphinx(audio).strip()
            except Exception:
                return None

    # -------------------------- Wake-word listener --------------------- #

    def start_wake_listener(self, on_wake: Callable[[str], None]) -> None:
        """Continuously listens; on 'hey spidy ...' calls on_wake(full_text)."""
        if not self.enabled_stt or self._listener_thread:
            return
        self._stop_flag.clear()
        self._listener_thread = threading.Thread(
            target=self._wake_loop, args=(on_wake,), daemon=True
        )
        self._listener_thread.start()

    def stop_wake_listener(self) -> None:
        self._stop_flag.set()
        self._listener_thread = None

    def pause(self) -> None:
        self._paused.set()

    def resume(self) -> None:
        self._paused.clear()

    def _wake_loop(self, on_wake: Callable[[str], None]) -> None:
        while not self._stop_flag.is_set():
            if self._paused.is_set() or self._speaking:
                time.sleep(0.3)
                continue
            try:
                with sr.Microphone() as mic:
                    self._recognizer.adjust_for_ambient_noise(mic, duration=0.25)
                    audio = self._recognizer.listen(
                        mic, timeout=MIC_LISTEN_TIMEOUT, phrase_time_limit=MIC_PHRASE_TIMEOUT
                    )
                text = ""
                try:
                    text = self._recognizer.recognize_google(audio).strip().lower()
                except Exception:
                    continue
                for wake in WAKE_WORDS:
                    if wake in text:
                        payload = text.split(wake, 1)[1].strip() or ""
                        on_wake(payload)
                        break
            except sr.WaitTimeoutError:
                continue
            except Exception:
                time.sleep(0.5)
                continue
