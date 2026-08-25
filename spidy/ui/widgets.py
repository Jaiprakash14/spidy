"""Reusable UI widgets - chat bubbles, sidebar buttons, status pill."""
from __future__ import annotations
from datetime import datetime

import customtkinter as ctk

from config import COLORS


class ChatBubble(ctk.CTkFrame):
    """A single message bubble aligned left (bot) or right (user)."""

    def __init__(self, parent, text: str, sender: str = "bot"):
        is_user = sender == "user"
        color = COLORS["user_bubble"] if is_user else COLORS["bot_bubble"]
        super().__init__(parent, fg_color="transparent")

        wrap = ctk.CTkFrame(self, fg_color=color, corner_radius=14)
        wrap.pack(anchor="e" if is_user else "w", padx=8, pady=4)

        label = ctk.CTkLabel(
            wrap,
            text=text,
            font=("Segoe UI", 12),
            text_color=COLORS["text"],
            justify="left",
            wraplength=560,
            anchor="w",
        )
        label.pack(padx=14, pady=(10, 4))

        meta = ctk.CTkLabel(
            wrap,
            text=f"{'You' if is_user else 'Spidy'} · {datetime.now().strftime('%H:%M')}",
            font=("Segoe UI", 9),
            text_color=COLORS["text_dim"],
        )
        meta.pack(padx=14, pady=(0, 8), anchor="e" if is_user else "w")


class SidebarButton(ctk.CTkButton):
    def __init__(self, parent, text: str, command, icon: str = "•"):
        super().__init__(
            parent,
            text=f"  {icon}   {text}",
            command=command,
            anchor="w",
            height=38,
            corner_radius=10,
            fg_color="transparent",
            hover_color=COLORS["panel_alt"],
            text_color=COLORS["text"],
            font=("Segoe UI", 12),
        )


class StatusPill(ctk.CTkFrame):
    """Small colored dot + label for showing Spidy's current state."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._dot = ctk.CTkLabel(self, text="●", font=("Segoe UI", 14), text_color=COLORS["success"])
        self._dot.pack(side="left", padx=(4, 6))
        self._text = ctk.CTkLabel(self, text="Idle · fully local", font=("Segoe UI", 11), text_color=COLORS["text_dim"])
        self._text.pack(side="left")

    def set(self, text: str, color_key: str = "success"):
        self._text.configure(text=text)
        self._dot.configure(text_color=COLORS.get(color_key, COLORS["success"]))
