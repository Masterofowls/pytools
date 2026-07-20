"""Clipboard helpers using only the Python standard library + OS tools."""

from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Callable


def copy_text(text: str) -> None:
    """Copy *text* to the system clipboard (no third-party packages)."""
    data = text.encode("utf-8")

    if sys.platform == "win32":
        _copy_windows(data)
        return
    if sys.platform == "darwin":
        _run_stdin(["pbcopy"], data)
        return

    # Linux / BSD: prefer Wayland, then X11.
    if shutil.which("wl-copy"):
        _run_stdin(["wl-copy", "--type", "text/plain"], data)
        return
    if shutil.which("xclip"):
        _run_stdin(["xclip", "-selection", "clipboard"], data)
        return
    if shutil.which("xsel"):
        _run_stdin(["xsel", "--clipboard", "--input"], data)
        return

    raise RuntimeError(
        "No clipboard tool found. On Linux install wl-clipboard, xclip, or xsel."
    )


def _copy_windows(data: bytes) -> None:
    # `clip` is always present on Windows; feed UTF-16LE so Unicode survives.
    completed = subprocess.run(
        ["clip"],
        input=data.decode("utf-8").encode("utf-16le"),
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or "Windows clip.exe failed")


def _run_stdin(cmd: list[str], data: bytes) -> None:
    completed = subprocess.run(cmd, input=data, check=False, capture_output=True)
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or f"{' '.join(cmd)} failed")


ClipboardFn = Callable[[str], None]
