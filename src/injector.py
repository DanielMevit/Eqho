"""Inject transcribed text into the currently focused application."""

import logging
import time

import pyperclip
from pynput.keyboard import Controller, Key

log = logging.getLogger(__name__)

_kb = Controller()


def type_text(text: str, *, use_clipboard: bool = True) -> None:
    """Send *text* to the active window.

    When *use_clipboard* is True (default), the text is pasted via the
    clipboard which is faster and handles Unicode reliably. Otherwise
    keystrokes are simulated character-by-character (slower, ASCII-safe).
    """
    if not text:
        return

    if use_clipboard:
        _paste_via_clipboard(text)
    else:
        _type_chars(text)


def _paste_via_clipboard(text: str) -> None:
    old = ""
    try:
        old = pyperclip.paste()
    except Exception:
        pass

    pyperclip.copy(text)
    time.sleep(0.05)

    _kb.press(Key.ctrl)
    _kb.press("v")
    _kb.release("v")
    _kb.release(Key.ctrl)
    time.sleep(0.1)

    try:
        pyperclip.copy(old)
    except Exception:
        pass


def _type_chars(text: str) -> None:
    for ch in text:
        try:
            _kb.type(ch)
            time.sleep(0.01)
        except Exception:
            log.debug("Could not type char %r", ch)
