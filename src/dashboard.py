"""Eqho Dashboard — main settings window.

A modern, themed settings dashboard with sidebar navigation.
Built on customtkinter for rounded widgets and native theme support.
"""

import logging
import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk

from .audio import list_input_devices, device_name
from .fonts import FONT_FAMILY
from .settings import (
    Settings, SUPPORTED_LANGUAGES, WHISPER_MODELS, HOTKEY_MODES,
    VOLUME_DUCK_OPTIONS, OVERLAY_POSITIONS, MODEL_CACHE_DIR,
)
from .theme import (
    get_colors, get_system_theme, ThemeColors, MODEL_INFO,
    RADIUS_SM, RADIUS_MD, RADIUS_LG, RADIUS_XL,
    FONT_SIZES, SPACING, ACCENT,
)

log = logging.getLogger(__name__)

# Window dimensions
WIN_W, WIN_H = 720, 520
SIDEBAR_W = 170


class Dashboard(ctk.CTkToplevel):
    """Main Eqho settings dashboard window."""

    def __init__(
        self,
        settings: Settings,
        on_settings_changed: Callable,
        parent: Optional[ctk.CTk] = None,
    ):
        # Create a hidden root if needed
        self._own_root = None
        if parent is None:
            self._own_root = ctk.CTk()
            self._own_root.withdraw()
            parent = self._own_root

        super().__init__(parent)
        self._settings = settings
        self._on_settings_changed = on_settings_changed
        self._colors: ThemeColors = get_colors(self._settings.theme)
        self._current_tab = "general"
        self._tab_frames: dict[str, ctk.CTkFrame] = {}
        self._hotkey_capturing = False
        self._hotkey_hook = None
        self._captured_keys: set[str] = set()

        self._setup_window()
        self._build_sidebar()
        self._build_content_area()
        self._build_all_tabs()
        self._show_tab("general")

        if self._own_root:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
            self._own_root.mainloop()

    def _setup_window(self) -> None:
        self.title("Eqho — Settings")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.minsize(WIN_W, WIN_H)
        self.resizable(False, False)
        self.attributes("-topmost", True)

        # Apply theme
        mode = self._settings.theme
        if mode == "system":
            mode = get_system_theme()
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("blue")

        self.configure(fg_color=self._colors.bg_primary)

        # Center on screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - WIN_W) // 2
        y = (sh - WIN_H) // 2
        self.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")

        self.grab_set()

    # -- Sidebar ---------------------------------------------------------------

    def _build_sidebar(self) -> None:
        self._sidebar = ctk.CTkFrame(
            self, width=SIDEBAR_W, corner_radius=0,
            fg_color=self._colors.bg_secondary,
            border_width=0,
        )
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Logo / title
        title_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        title_frame.pack(fill="x", padx=SPACING["lg"], pady=(SPACING["xl"], SPACING["lg"]))

        ctk.CTkLabel(
            title_frame, text="Eqho",
            font=(FONT_FAMILY, FONT_SIZES["xl"], "bold"),
            text_color=self._colors.fg_primary,
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame, text="Settings",
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            text_color=self._colors.fg_secondary,
        ).pack(anchor="w")

        # Nav items
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        tabs = [
            ("general", "General"),
            ("overlay", "Overlay"),
            ("models", "Models"),
            ("history", "History"),
            ("about", "About"),
        ]

        for key, label in tabs:
            btn = ctk.CTkButton(
                self._sidebar,
                text=label,
                font=(FONT_FAMILY, FONT_SIZES["base"]),
                height=36,
                corner_radius=RADIUS_SM,
                fg_color="transparent",
                text_color=self._colors.fg_secondary,
                hover_color=self._colors.bg_hover,
                anchor="w",
                command=lambda k=key: self._show_tab(k),
            )
            btn.pack(fill="x", padx=SPACING["sm"], pady=2)
            self._nav_buttons[key] = btn

        # Spacer
        ctk.CTkFrame(self._sidebar, fg_color="transparent", height=1).pack(expand=True)

        # Theme switcher at bottom
        self._build_theme_switcher()

    def _build_theme_switcher(self) -> None:
        frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        frame.pack(fill="x", padx=SPACING["sm"], pady=(0, SPACING["lg"]))

        ctk.CTkLabel(
            frame, text="Theme",
            font=(FONT_FAMILY, FONT_SIZES["xs"]),
            text_color=self._colors.fg_muted,
        ).pack(anchor="w", padx=SPACING["sm"], pady=(0, 4))

        pill = ctk.CTkFrame(
            frame, corner_radius=RADIUS_MD,
            fg_color=self._colors.bg_tertiary,
            height=32,
        )
        pill.pack(fill="x", padx=4)
        pill.pack_propagate(False)

        # Three segments: Light, Dark, System
        self._theme_buttons: dict[str, ctk.CTkButton] = {}
        for mode, label in [("light", "☀"), ("dark", "🌙"), ("system", "💻")]:
            is_active = self._settings.theme == mode
            btn = ctk.CTkButton(
                pill,
                text=label,
                width=40,
                height=26,
                corner_radius=RADIUS_SM,
                font=(FONT_FAMILY, FONT_SIZES["base"]),
                fg_color=self._colors.accent if is_active else "transparent",
                text_color=self._colors.bg_primary if is_active else self._colors.fg_secondary,
                hover_color=self._colors.bg_hover,
                command=lambda m=mode: self._set_theme(m),
            )
            btn.pack(side="left", expand=True, fill="both", padx=2, pady=2)
            self._theme_buttons[mode] = btn

    def _set_theme(self, mode: str) -> None:
        self._settings.theme = mode
        self._settings.save()

        # Update appearance
        resolved = mode if mode != "system" else get_system_theme()
        ctk.set_appearance_mode(resolved)
        self._colors = get_colors(mode)

        # Update pill buttons
        for m, btn in self._theme_buttons.items():
            is_active = m == mode
            btn.configure(
                fg_color=self._colors.accent if is_active else "transparent",
                text_color=self._colors.bg_primary if is_active else self._colors.fg_secondary,
            )

        self._apply_settings(reload_model=False)

    # -- Content area ----------------------------------------------------------

    def _build_content_area(self) -> None:
        self._content = ctk.CTkFrame(
            self, fg_color=self._colors.bg_primary,
            corner_radius=0, border_width=0,
        )
        self._content.pack(side="right", fill="both", expand=True)

    def _show_tab(self, key: str) -> None:
        self._current_tab = key
        # Update nav highlight
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=self._colors.accent_muted,
                    text_color=self._colors.accent,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self._colors.fg_secondary,
                )
        # Show the right frame
        for k, frame in self._tab_frames.items():
            if k == key:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

    def _build_all_tabs(self) -> None:
        self._build_general_tab()
        self._build_overlay_tab()
        self._build_models_tab()
        self._build_history_tab()
        self._build_about_tab()

    # -- Helpers for building UI -----------------------------------------------

    def _make_tab_frame(self, key: str) -> ctk.CTkScrollableFrame:
        frame = ctk.CTkScrollableFrame(
            self._content,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self._colors.bg_tertiary,
            scrollbar_button_hover_color=self._colors.bg_hover,
        )
        self._tab_frames[key] = frame
        return frame

    def _section_label(self, parent, text: str) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(
            parent, text=text,
            font=(FONT_FAMILY, FONT_SIZES["xs"]),
            text_color=self._colors.fg_muted,
            anchor="w",
        )
        lbl.pack(fill="x", padx=SPACING["xl"], pady=(SPACING["lg"], 2))
        return lbl

    def _card(self, parent) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent,
            corner_radius=RADIUS_MD,
            fg_color=self._colors.bg_secondary,
            border_width=1,
            border_color=self._colors.border_subtle,
        )
        card.pack(fill="x", padx=SPACING["xl"], pady=(SPACING["xs"], 0))
        return card

    def _setting_row(self, parent, label: str, description: str = "") -> ctk.CTkFrame:
        """A row inside a card: label on the left, widget slot on the right."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left, text=label,
            font=(FONT_FAMILY, FONT_SIZES["base"]),
            text_color=self._colors.fg_primary,
            anchor="w",
        ).pack(anchor="w")

        if description:
            ctk.CTkLabel(
                left, text=description,
                font=(FONT_FAMILY, FONT_SIZES["xs"]),
                text_color=self._colors.fg_muted,
                anchor="w",
            ).pack(anchor="w")

        right = ctk.CTkFrame(row, fg_color="transparent")
        right.pack(side="right")
        return right

    # ==========================================================================
    # GENERAL TAB
    # ==========================================================================

    def _build_general_tab(self) -> None:
        tab = self._make_tab_frame("general")

        # Header
        ctk.CTkLabel(
            tab, text="General",
            font=(FONT_FAMILY, FONT_SIZES["2xl"], "bold"),
            text_color=self._colors.fg_primary,
            anchor="w",
        ).pack(fill="x", padx=SPACING["xl"], pady=(SPACING["xl"], SPACING["xs"]))

        ctk.CTkLabel(
            tab, text="Core settings for dictation",
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            text_color=self._colors.fg_secondary,
            anchor="w",
        ).pack(fill="x", padx=SPACING["xl"], pady=(0, SPACING["md"]))

        # -- Microphone --------------------------------------------------------
        self._section_label(tab, "AUDIO INPUT")
        card = self._card(tab)
        right = self._setting_row(card, "Microphone", "Select your input device")

        devices = list_input_devices()
        device_names = ["System Default"] + [name for _, name in devices]
        device_indices = [None] + [idx for idx, _ in devices]

        current_idx = self._settings.audio_device
        current_name = "System Default"
        for idx, name in devices:
            if idx == current_idx:
                current_name = name
                break

        self._mic_var = ctk.StringVar(value=current_name)
        mic_menu = ctk.CTkOptionMenu(
            right,
            variable=self._mic_var,
            values=device_names,
            width=200,
            height=30,
            corner_radius=RADIUS_SM,
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            dropdown_font=(FONT_FAMILY, FONT_SIZES["sm"]),
            command=lambda val: self._on_mic_changed(val, device_names, device_indices),
        )
        mic_menu.pack()

        # -- Hotkey ------------------------------------------------------------
        self._section_label(tab, "HOTKEY")
        card = self._card(tab)

        # Hotkey display row
        hotkey_row = ctk.CTkFrame(card, fg_color="transparent")
        hotkey_row.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])

        left = ctk.CTkFrame(hotkey_row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            left, text="Global Hotkey",
            font=(FONT_FAMILY, FONT_SIZES["base"]),
            text_color=self._colors.fg_primary, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            left, text="Press to activate/deactivate dictation",
            font=(FONT_FAMILY, FONT_SIZES["xs"]),
            text_color=self._colors.fg_muted, anchor="w",
        ).pack(anchor="w")

        hotkey_right = ctk.CTkFrame(hotkey_row, fg_color="transparent")
        hotkey_right.pack(side="right")

        self._hotkey_display = ctk.CTkButton(
            hotkey_right,
            text=self._format_hotkey(self._settings.hotkey),
            font=(FONT_FAMILY, FONT_SIZES["lg"], "bold"),
            width=160, height=36,
            corner_radius=RADIUS_SM,
            fg_color=self._colors.bg_tertiary,
            text_color=self._colors.accent,
            hover_color=self._colors.bg_hover,
            border_width=1,
            border_color=self._colors.border,
            command=self._start_hotkey_capture,
        )
        self._hotkey_display.pack()

        self._hotkey_hint = ctk.CTkLabel(
            hotkey_right, text="Click to change",
            font=(FONT_FAMILY, FONT_SIZES["xs"]),
            text_color=self._colors.fg_muted,
        )
        self._hotkey_hint.pack(pady=(2, 0))

        # Hotkey mode
        right = self._setting_row(card, "Hotkey Mode", "Toggle on/off or hold to talk")
        self._mode_var = ctk.StringVar(value=self._settings.hotkey_mode)
        mode_menu = ctk.CTkSegmentedButton(
            right,
            values=["toggle", "hold"],
            variable=self._mode_var,
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            corner_radius=RADIUS_SM,
            command=self._on_mode_changed,
        )
        mode_menu.pack()

        # -- Model quick select ------------------------------------------------
        self._section_label(tab, "MODEL")
        card = self._card(tab)

        model_row = ctk.CTkFrame(card, fg_color="transparent")
        model_row.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])

        model_left = ctk.CTkFrame(model_row, fg_color="transparent")
        model_left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            model_left, text="Whisper Model",
            font=(FONT_FAMILY, FONT_SIZES["base"]),
            text_color=self._colors.fg_primary, anchor="w",
        ).pack(anchor="w")

        self._model_info_label = ctk.CTkLabel(
            model_left, text=self._get_model_info_text(self._settings.model_size),
            font=(FONT_FAMILY, FONT_SIZES["xs"]),
            text_color=self._colors.fg_muted, anchor="w",
        )
        self._model_info_label.pack(anchor="w")

        model_right = ctk.CTkFrame(model_row, fg_color="transparent")
        model_right.pack(side="right")

        model_display_names = [MODEL_INFO[k]["name"] for k in WHISPER_MODELS]
        model_keys = list(WHISPER_MODELS.keys())
        current_model_name = MODEL_INFO.get(self._settings.model_size, {}).get("name", "Unknown")

        self._model_var = ctk.StringVar(value=current_model_name)
        self._model_keys = model_keys
        self._model_display_names = model_display_names

        model_menu = ctk.CTkOptionMenu(
            model_right,
            variable=self._model_var,
            values=model_display_names,
            width=180,
            height=30,
            corner_radius=RADIUS_SM,
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            dropdown_font=(FONT_FAMILY, FONT_SIZES["sm"]),
            command=self._on_model_changed,
        )
        model_menu.pack()

        # -- Volume & Paste ----------------------------------------------------
        self._section_label(tab, "BEHAVIOR")
        card = self._card(tab)

        # Volume while speaking
        right = self._setting_row(card, "Volume While Speaking", "System volume during dictation")
        duck_labels = {"off": "Off", "50%": "50%", "25%": "25%", "10%": "10%", "mute": "Mute"}
        self._duck_var = ctk.StringVar(value=duck_labels.get(self._settings.volume_duck, "Mute"))
        duck_menu = ctk.CTkOptionMenu(
            right,
            variable=self._duck_var,
            values=list(duck_labels.values()),
            width=100, height=30,
            corner_radius=RADIUS_SM,
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            dropdown_font=(FONT_FAMILY, FONT_SIZES["sm"]),
            command=lambda val: self._on_duck_changed(val, duck_labels),
        )
        duck_menu.pack()

        # Paste mode
        right = self._setting_row(card, "Paste Mode", "How text is injected into apps")
        self._paste_var = ctk.StringVar(value="Clipboard" if self._settings.auto_paste else "Typing")
        paste_menu = ctk.CTkSegmentedButton(
            right,
            values=["Clipboard", "Typing"],
            variable=self._paste_var,
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            corner_radius=RADIUS_SM,
            command=self._on_paste_changed,
        )
        paste_menu.pack()

        # Language
        right = self._setting_row(card, "Language", "Transcription language")
        lang_names = list(SUPPORTED_LANGUAGES.values())
        lang_codes = list(SUPPORTED_LANGUAGES.keys())
        current_lang = SUPPORTED_LANGUAGES.get(self._settings.language, "English")
        self._lang_var = ctk.StringVar(value=current_lang)
        self._lang_codes = lang_codes
        self._lang_names = lang_names

        lang_menu = ctk.CTkOptionMenu(
            right,
            variable=self._lang_var,
            values=lang_names,
            width=140, height=30,
            corner_radius=RADIUS_SM,
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            dropdown_font=(FONT_FAMILY, FONT_SIZES["sm"]),
            command=self._on_lang_changed,
        )
        lang_menu.pack()

        # Start with Windows
        right = self._setting_row(card, "Start with Windows", "Launch Eqho on login")
        self._startup_var = ctk.BooleanVar(value=self._settings.start_with_windows)
        startup_switch = ctk.CTkSwitch(
            right,
            text="",
            variable=self._startup_var,
            onvalue=True, offvalue=False,
            command=self._on_startup_changed,
            width=44, height=22,
        )
        startup_switch.pack()

    # -- General tab callbacks -------------------------------------------------

    def _format_hotkey(self, combo: str) -> str:
        return " + ".join(p.strip().title() for p in combo.split("+"))

    def _get_model_info_text(self, model_key: str) -> str:
        info = MODEL_INFO.get(model_key, {})
        icon = info.get("icon", "")
        lang = info.get("lang", "")
        size = info.get("size", "")
        device = info.get("device", "")
        rec = info.get("rec", "")
        cached = self._is_model_cached(model_key)
        status = "Downloaded" if cached else "Not downloaded"
        return f"{icon} {lang} · {size} · {device}\n{rec} · {status}"

    def _is_model_cached(self, model_key: str) -> bool:
        for candidate in [
            MODEL_CACHE_DIR / model_key,
            MODEL_CACHE_DIR / f"models--Systran--faster-whisper-{model_key}",
            MODEL_CACHE_DIR / f"models--ctranslate2-4you--distil-whisper-{model_key}",
            MODEL_CACHE_DIR / "huggingface" / f"models--Systran--faster-whisper-{model_key}",
            MODEL_CACHE_DIR / "huggingface" / f"models--ctranslate2-4you--distil-whisper-{model_key}",
        ]:
            if candidate.exists():
                return True
        return False

    def _apply_settings(self, reload_model: bool = False) -> None:
        """Run settings callback in background to avoid freezing the dashboard."""
        threading.Thread(
            target=self._on_settings_changed,
            kwargs={"reload_model": reload_model},
            daemon=True,
        ).start()

    def _on_mic_changed(self, val, names, indices) -> None:
        idx = indices[names.index(val)] if val in names else None
        self._settings.audio_device = idx
        self._settings.save()
        self._apply_settings(reload_model=True)

    def _on_mode_changed(self, val) -> None:
        self._settings.hotkey_mode = val
        self._settings.save()
        self._apply_settings(reload_model=False)

    def _on_model_changed(self, display_name) -> None:
        idx = self._model_display_names.index(display_name)
        key = self._model_keys[idx]
        if key != self._settings.model_size:
            self._settings.model_size = key
            self._settings.save()
            self._model_info_label.configure(text=self._get_model_info_text(key))
            self._apply_settings(reload_model=True)

    def _on_duck_changed(self, val, labels) -> None:
        reverse = {v: k for k, v in labels.items()}
        key = reverse.get(val, "mute")
        self._settings.volume_duck = key
        self._settings.save()

    def _on_paste_changed(self, val) -> None:
        self._settings.auto_paste = val == "Clipboard"
        self._settings.save()

    def _on_lang_changed(self, val) -> None:
        idx = self._lang_names.index(val)
        code = self._lang_codes[idx]
        self._settings.language = code
        self._settings.save()
        self._apply_settings(reload_model=True)

    def _on_startup_changed(self) -> None:
        enabled = self._startup_var.get()
        self._settings.start_with_windows = enabled
        self._settings.save()
        # Update registry
        try:
            import winreg
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                                winreg.KEY_SET_VALUE | winreg.KEY_READ) as key:
                if enabled:
                    if getattr(sys, "frozen", False):
                        cmd = f'"{sys.executable}"'
                    else:
                        cmd = f'"{sys.executable}" "{Path(sys.argv[0]).resolve()}"'
                    winreg.SetValueEx(key, "Eqho", 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(key, "Eqho")
                    except FileNotFoundError:
                        pass
        except Exception as e:
            log.error("Failed to update startup registry: %s", e)

    # -- Hotkey capture --------------------------------------------------------

    def _start_hotkey_capture(self) -> None:
        if self._hotkey_capturing:
            return
        import keyboard
        self._hotkey_capturing = True
        self._captured_keys.clear()
        self._hotkey_display.configure(
            text="Press a key combo...",
            fg_color=self._colors.accent_muted,
            text_color=self._colors.danger,
        )
        self._hotkey_hint.configure(text="Esc to cancel")
        self._hotkey_hook = keyboard.hook(self._on_hotkey_event, suppress=False)

    def _on_hotkey_event(self, event) -> None:
        import keyboard as kb
        name = event.name.lower() if event.name else ""
        if name == "esc":
            self._stop_hotkey_capture(cancelled=True)
            return

        if event.event_type == kb.KEY_DOWN:
            self._captured_keys.add(name)
            combo = self._keys_to_combo(self._captured_keys)
            try:
                self.after(0, lambda: self._hotkey_display.configure(
                    text=self._format_hotkey(combo), text_color=self._colors.accent))
            except Exception:
                pass
        elif event.event_type == kb.KEY_UP:
            if self._captured_keys:
                combo = self._keys_to_combo(self._captured_keys)
                self._settings.hotkey = combo
                self._settings.save()
                self._stop_hotkey_capture(cancelled=False)
                self._apply_settings(reload_model=False)

    def _keys_to_combo(self, keys: set[str]) -> str:
        mod_names = {"ctrl", "left ctrl", "right ctrl", "alt", "left alt", "right alt",
                     "shift", "left shift", "right shift", "left windows", "right windows"}
        mod_map = {
            "left ctrl": "ctrl", "right ctrl": "ctrl",
            "left alt": "alt", "right alt": "alt",
            "left shift": "shift", "right shift": "shift",
            "left windows": "win", "right windows": "win",
        }
        modifiers, regular = [], []
        for k in keys:
            if k in mod_names:
                canonical = mod_map.get(k, k)
                if canonical not in modifiers:
                    modifiers.append(canonical)
            else:
                regular.append(k)
        mod_order = {"ctrl": 0, "alt": 1, "shift": 2, "win": 3}
        modifiers.sort(key=lambda m: mod_order.get(m, 9))
        return "+".join(modifiers + regular)

    def _stop_hotkey_capture(self, cancelled: bool) -> None:
        import keyboard
        self._hotkey_capturing = False
        if self._hotkey_hook is not None:
            try:
                keyboard.unhook(self._hotkey_hook)
            except Exception:
                pass
            self._hotkey_hook = None

        combo = self._settings.hotkey
        try:
            self.after(0, lambda: [
                self._hotkey_display.configure(
                    text=self._format_hotkey(combo),
                    fg_color=self._colors.bg_tertiary,
                    text_color=self._colors.accent,
                ),
                self._hotkey_hint.configure(text="Click to change"),
            ])
        except Exception:
            pass

    # ==========================================================================
    # OVERLAY TAB
    # ==========================================================================

    def _build_overlay_tab(self) -> None:
        tab = self._make_tab_frame("overlay")

        ctk.CTkLabel(
            tab, text="Overlay",
            font=(FONT_FAMILY, FONT_SIZES["2xl"], "bold"),
            text_color=self._colors.fg_primary, anchor="w",
        ).pack(fill="x", padx=SPACING["xl"], pady=(SPACING["xl"], SPACING["xs"]))

        ctk.CTkLabel(
            tab, text="Floating transcription preview bar",
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            text_color=self._colors.fg_secondary, anchor="w",
        ).pack(fill="x", padx=SPACING["xl"], pady=(0, SPACING["md"]))

        # Enable switch
        self._section_label(tab, "VISIBILITY")
        card = self._card(tab)
        right = self._setting_row(card, "Show Overlay", "Display transcription text while dictating")
        self._overlay_var = ctk.BooleanVar(value=self._settings.overlay_enabled)
        ctk.CTkSwitch(
            right, text="", variable=self._overlay_var,
            onvalue=True, offvalue=False,
            command=self._on_overlay_toggle,
            width=44, height=22,
        ).pack()

        # Position
        self._section_label(tab, "POSITION")
        card = self._card(tab)
        right = self._setting_row(card, "Screen Position", "Where the overlay appears")

        pos_labels = {
            "bottom-center": "Bottom Center", "top-center": "Top Center",
            "top-left": "Top Left", "top-right": "Top Right",
            "bottom-left": "Bottom Left", "bottom-right": "Bottom Right",
        }
        current_pos = pos_labels.get(self._settings.overlay_position, "Bottom Center")
        self._pos_var = ctk.StringVar(value=current_pos)

        ctk.CTkOptionMenu(
            right, variable=self._pos_var,
            values=list(pos_labels.values()),
            width=160, height=30,
            corner_radius=RADIUS_SM,
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            dropdown_font=(FONT_FAMILY, FONT_SIZES["sm"]),
            command=lambda v: self._on_pos_changed(v, pos_labels),
        ).pack()

        # Appearance
        self._section_label(tab, "APPEARANCE")
        card = self._card(tab)

        # Opacity slider
        opacity_row = ctk.CTkFrame(card, fg_color="transparent")
        opacity_row.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])

        ctk.CTkLabel(
            opacity_row, text="Opacity",
            font=(FONT_FAMILY, FONT_SIZES["base"]),
            text_color=self._colors.fg_primary, anchor="w",
        ).pack(anchor="w")

        slider_frame = ctk.CTkFrame(opacity_row, fg_color="transparent")
        slider_frame.pack(fill="x")

        self._opacity_val_label = ctk.CTkLabel(
            slider_frame,
            text=f"{int(self._settings.overlay_opacity * 100)}%",
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            text_color=self._colors.fg_secondary,
            width=40,
        )
        self._opacity_val_label.pack(side="right", padx=(SPACING["sm"], 0))

        ctk.CTkSlider(
            slider_frame,
            from_=0.3, to=1.0,
            number_of_steps=14,
            command=self._on_opacity_changed,
            height=16,
        ).pack(side="left", fill="x", expand=True)

        # Font size slider
        font_row = ctk.CTkFrame(card, fg_color="transparent")
        font_row.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])

        ctk.CTkLabel(
            font_row, text="Font Size",
            font=(FONT_FAMILY, FONT_SIZES["base"]),
            text_color=self._colors.fg_primary, anchor="w",
        ).pack(anchor="w")

        fs_frame = ctk.CTkFrame(font_row, fg_color="transparent")
        fs_frame.pack(fill="x")

        self._fontsize_val_label = ctk.CTkLabel(
            fs_frame,
            text=f"{self._settings.overlay_font_size}px",
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            text_color=self._colors.fg_secondary,
            width=40,
        )
        self._fontsize_val_label.pack(side="right", padx=(SPACING["sm"], 0))

        ctk.CTkSlider(
            fs_frame,
            from_=10, to=28,
            number_of_steps=18,
            command=self._on_fontsize_changed,
            height=16,
        ).pack(side="left", fill="x", expand=True)

    def _on_overlay_toggle(self) -> None:
        self._settings.overlay_enabled = self._overlay_var.get()
        self._settings.save()

    def _on_pos_changed(self, val, labels) -> None:
        reverse = {v: k for k, v in labels.items()}
        key = reverse.get(val, "bottom-center")
        self._settings.overlay_position = key
        self._settings.save()

    def _on_opacity_changed(self, val) -> None:
        self._settings.overlay_opacity = round(val, 2)
        self._settings.save()
        self._opacity_val_label.configure(text=f"{int(val * 100)}%")

    def _on_fontsize_changed(self, val) -> None:
        self._settings.overlay_font_size = int(val)
        self._settings.save()
        self._fontsize_val_label.configure(text=f"{int(val)}px")

    # ==========================================================================
    # MODELS TAB
    # ==========================================================================

    def _build_models_tab(self) -> None:
        tab = self._make_tab_frame("models")

        ctk.CTkLabel(
            tab, text="Models",
            font=(FONT_FAMILY, FONT_SIZES["2xl"], "bold"),
            text_color=self._colors.fg_primary, anchor="w",
        ).pack(fill="x", padx=SPACING["xl"], pady=(SPACING["xl"], SPACING["xs"]))

        ctk.CTkLabel(
            tab, text="Whisper models for speech recognition",
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            text_color=self._colors.fg_secondary, anchor="w",
        ).pack(fill="x", padx=SPACING["xl"], pady=(0, SPACING["md"]))

        # English-optimized section
        self._section_label(tab, "ENGLISH OPTIMIZED")
        for key in ["distil-large-v3", "distil-medium.en", "distil-small.en"]:
            self._build_model_card(tab, key)

        # Multilingual section
        self._section_label(tab, "MULTILINGUAL")
        for key in ["large-v3-turbo", "medium", "small", "base", "tiny", "large-v3"]:
            self._build_model_card(tab, key)

    def _build_model_card(self, parent, model_key: str) -> None:
        info = MODEL_INFO.get(model_key, {})
        is_selected = self._settings.model_size == model_key
        cached = self._is_model_cached(model_key)

        card = ctk.CTkFrame(
            parent,
            corner_radius=RADIUS_MD,
            fg_color=self._colors.bg_secondary,
            border_width=2 if is_selected else 1,
            border_color=self._colors.accent if is_selected else self._colors.border_subtle,
        )
        card.pack(fill="x", padx=SPACING["xl"], pady=(SPACING["xs"], 0))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])

        # Top line: name + status
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        name_text = info.get("name", model_key)
        if is_selected:
            name_text += "  ●"

        ctk.CTkLabel(
            top, text=name_text,
            font=(FONT_FAMILY, FONT_SIZES["base"], "bold"),
            text_color=self._colors.accent if is_selected else self._colors.fg_primary,
            anchor="w",
        ).pack(side="left")

        # Status badge
        status_text = "✓ Ready" if cached else "↓ Download"
        status_color = self._colors.success if cached else self._colors.fg_muted
        ctk.CTkLabel(
            top, text=status_text,
            font=(FONT_FAMILY, FONT_SIZES["xs"]),
            text_color=status_color,
        ).pack(side="right")

        # Info line
        detail = f"{info.get('lang', '')} · {info.get('size', '')} · {info.get('device', '')}"
        ctk.CTkLabel(
            inner, text=detail,
            font=(FONT_FAMILY, FONT_SIZES["xs"]),
            text_color=self._colors.fg_secondary, anchor="w",
        ).pack(fill="x")

        # Recommendation
        rec = info.get("rec", "")
        if rec:
            ctk.CTkLabel(
                inner, text=rec,
                font=(FONT_FAMILY, FONT_SIZES["xs"]),
                text_color=self._colors.fg_muted, anchor="w",
            ).pack(fill="x")

        # Select button (if not already selected)
        if not is_selected:
            ctk.CTkButton(
                inner, text="Select",
                font=(FONT_FAMILY, FONT_SIZES["xs"]),
                width=70, height=24,
                corner_radius=RADIUS_SM,
                command=lambda k=model_key: self._select_model_from_card(k),
            ).pack(anchor="e", pady=(SPACING["xs"], 0))

    def _select_model_from_card(self, key: str) -> None:
        self._settings.model_size = key
        self._settings.save()
        # Update the general tab dropdown
        name = MODEL_INFO.get(key, {}).get("name", key)
        self._model_var.set(name)
        self._model_info_label.configure(text=self._get_model_info_text(key))
        # Rebuild models tab to update selection highlight
        self._tab_frames["models"].pack_forget()
        self._tab_frames.pop("models")
        self._build_models_tab()
        if self._current_tab == "models":
            self._tab_frames["models"].pack(fill="both", expand=True)
        self._apply_settings(reload_model=True)

    # ==========================================================================
    # HISTORY TAB (placeholder)
    # ==========================================================================

    def _build_history_tab(self) -> None:
        tab = self._make_tab_frame("history")

        ctk.CTkLabel(
            tab, text="History",
            font=(FONT_FAMILY, FONT_SIZES["2xl"], "bold"),
            text_color=self._colors.fg_primary, anchor="w",
        ).pack(fill="x", padx=SPACING["xl"], pady=(SPACING["xl"], SPACING["xs"]))

        ctk.CTkLabel(
            tab, text="Transcript history log",
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            text_color=self._colors.fg_secondary, anchor="w",
        ).pack(fill="x", padx=SPACING["xl"], pady=(0, SPACING["2xl"]))

        # Coming soon card
        card = self._card(tab)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING["xl"], pady=SPACING["2xl"])

        ctk.CTkLabel(
            inner, text="Coming in Phase 3",
            font=(FONT_FAMILY, FONT_SIZES["lg"], "bold"),
            text_color=self._colors.fg_muted,
        ).pack()

        ctk.CTkLabel(
            inner, text="Your past dictations will be saved and searchable here.",
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            text_color=self._colors.fg_muted,
        ).pack(pady=(SPACING["xs"], 0))

        # Planned features
        self._section_label(tab, "PLANNED FEATURES")
        card = self._card(tab)
        planned = [
            ("Transcript Log", "Save all dictations to a local searchable file"),
            ("Voice Commands", '"New line", "period", "delete that"'),
            ("Sound Feedback", "Subtle chime on start/stop"),
            ("Per-App Paste Rules", "Some apps need typing instead of clipboard"),
        ]
        for title, desc in planned:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=SPACING["lg"], pady=SPACING["xs"])
            ctk.CTkLabel(
                row, text=f"○  {title}",
                font=(FONT_FAMILY, FONT_SIZES["sm"]),
                text_color=self._colors.fg_muted, anchor="w",
            ).pack(anchor="w")
            ctk.CTkLabel(
                row, text=f"     {desc}",
                font=(FONT_FAMILY, FONT_SIZES["xs"]),
                text_color=self._colors.fg_muted, anchor="w",
            ).pack(anchor="w")

    # ==========================================================================
    # ABOUT TAB
    # ==========================================================================

    def _build_about_tab(self) -> None:
        tab = self._make_tab_frame("about")

        ctk.CTkLabel(
            tab, text="About Eqho",
            font=(FONT_FAMILY, FONT_SIZES["2xl"], "bold"),
            text_color=self._colors.fg_primary, anchor="w",
        ).pack(fill="x", padx=SPACING["xl"], pady=(SPACING["xl"], SPACING["xs"]))

        ctk.CTkLabel(
            tab, text="Your voice, everywhere.",
            font=(FONT_FAMILY, FONT_SIZES["sm"]),
            text_color=self._colors.fg_secondary, anchor="w",
        ).pack(fill="x", padx=SPACING["xl"], pady=(0, SPACING["md"]))

        card = self._card(tab)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING["lg"], pady=SPACING["lg"])

        details = [
            ("Version", "0.3.0"),
            ("Engine", "faster-whisper (CTranslate2)"),
            ("Default Model", "Distil Large v3"),
            ("GPU", "CUDA (NVIDIA) with CPU fallback"),
            ("Platform", "Windows 10/11"),
            ("Font", "Inter (SIL Open Font License)"),
            ("Author", "Daniel Mevit"),
        ]
        for label, value in details:
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                row, text=label,
                font=(FONT_FAMILY, FONT_SIZES["sm"]),
                text_color=self._colors.fg_secondary, anchor="w",
                width=120,
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=value,
                font=(FONT_FAMILY, FONT_SIZES["sm"]),
                text_color=self._colors.fg_primary, anchor="w",
            ).pack(side="left")

        # Credits
        self._section_label(tab, "POWERED BY")
        card = self._card(tab)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])

        techs = [
            "faster-whisper — Fast Whisper inference (MIT)",
            "customtkinter — Modern tkinter widgets",
            "pystray — System tray integration",
            "keyboard — Global hotkey capture",
            "pycaw — Windows audio control",
        ]
        for t in techs:
            ctk.CTkLabel(
                inner, text=f"·  {t}",
                font=(FONT_FAMILY, FONT_SIZES["xs"]),
                text_color=self._colors.fg_secondary, anchor="w",
            ).pack(anchor="w", pady=1)

    # -- Lifecycle -------------------------------------------------------------

    def _on_close(self) -> None:
        global _active_dashboard
        _active_dashboard = None
        if self._hotkey_capturing:
            self._stop_hotkey_capture(cancelled=True)
        try:
            self.grab_release()
            self.destroy()
        except Exception:
            pass
        if self._own_root:
            try:
                self._own_root.destroy()
            except Exception:
                pass


# Singleton tracking
_active_dashboard: Optional[Dashboard] = None
_dashboard_lock = threading.Lock()


def open_dashboard(settings: Settings, on_settings_changed: Callable) -> None:
    """Open the dashboard, or focus the existing one if already open."""
    global _active_dashboard

    with _dashboard_lock:
        if _active_dashboard is not None:
            try:
                _active_dashboard.after(0, lambda: (
                    _active_dashboard.deiconify(),
                    _active_dashboard.lift(),
                    _active_dashboard.focus_force(),
                ))
                return
            except Exception:
                _active_dashboard = None

    def _run():
        global _active_dashboard
        dash = Dashboard(settings, on_settings_changed)
        _active_dashboard = dash

    threading.Thread(target=_run, daemon=True).start()
