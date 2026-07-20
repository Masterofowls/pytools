"""Clipboard helpers for the interactive client."""

from __future__ import annotations

from collections.abc import Callable


def copy_text(text: str) -> None:
    """Copy *text* to the system clipboard via pyperclip."""
    import pyperclip  # type: ignore[import-untyped]

    pyperclip.copy(text)


ClipboardFn = Callable[[str], None]
