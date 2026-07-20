"""Interactive client for code → markdown conversion."""

from __future__ import annotations

import sys
from pathlib import Path

from code_md.clipboard import ClipboardFn, copy_text
from code_md.detect import detect_language
from code_md.fence import to_markdown

_PASTE_SENTINEL = "END"
_DEFAULT_OUTPUT_DIR = Path("output")
_DEFAULT_OUTPUT_NAME = "snippet.md"


class InteractiveApp:
    """Guided terminal client: paste text or load a .txt file."""

    def __init__(
        self,
        *,
        stdin: object = sys.stdin,
        stdout: object = sys.stdout,
        stderr: object = sys.stderr,
        output_dir: Path | None = None,
        clipboard: ClipboardFn | None = None,
    ) -> None:
        self._in = stdin
        self._out = stdout
        self._err = stderr
        self._output_dir = output_dir or _DEFAULT_OUTPUT_DIR
        self._clipboard = clipboard or copy_text

    def run(self) -> int:
        self._println("=" * 48)
        self._println("  code-md  ·  Markdown code-snippet client")
        self._println("=" * 48)
        self._println("")
        self._println("How do you want to provide the code?")
        self._println("  [1] Paste inline text")
        self._println("  [2] Load a .txt file")
        self._println("  [q] Quit")
        self._println("")

        choice = self._ask("Choice (1/2/q): ").strip().lower()
        if choice in {"q", "quit", "exit"}:
            self._println("Bye.")
            return 0
        if choice == "1":
            code, filename = self._paste_inline(), None
        elif choice == "2":
            loaded = self._load_txt_file()
            if loaded is None:
                return 1
            code, filename = loaded
        else:
            self._eprintln(f"error: invalid choice {choice!r} (use 1, 2, or q)")
            return 1

        if not code.strip():
            self._eprintln("error: no code provided.")
            return 1

        language = detect_language(code, filename=filename)
        markdown = to_markdown(code, filename=filename)

        self._println("")
        self._println(f"Detected language: {language}")
        self._println("-" * 48)
        self._print(markdown)
        self._println("-" * 48)

        if not self._deliver(markdown):
            return 1

        self._println("Done.")
        return 0

    def _deliver(self, markdown: str) -> bool:
        self._println("")
        self._println("Where should the markdown go?")
        self._println(f"  [1] Save .md file under {self._output_dir}/")
        self._println("  [2] Copy to clipboard")
        self._println("  [3] Both (file + clipboard)")
        self._println("  [4] Skip (screen only)")
        self._println("")

        choice = self._ask("Choice (1/2/3/4): ").strip().lower()
        save_file = choice in {"1", "3"}
        to_clip = choice in {"2", "3"}

        if choice == "4":
            return True
        if choice not in {"1", "2", "3"}:
            self._eprintln(f"error: invalid choice {choice!r} (use 1, 2, 3, or 4)")
            return False

        if save_file:
            out_path = self._ask_output_path()
            if out_path is None:
                return False
            try:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(markdown, encoding="utf-8")
            except OSError as exc:
                self._eprintln(f"error: could not save file: {exc}")
                return False
            self._println(f"Saved: {out_path.resolve()}")

        if to_clip:
            try:
                self._clipboard(markdown)
            except Exception as exc:  # noqa: BLE001 — surface clipboard failures cleanly
                self._eprintln(f"error: clipboard copy failed: {exc}")
                return False
            self._println("Copied to clipboard.")

        return True

    def _paste_inline(self) -> str:
        self._println("")
        self._println(f"Paste your text below. Finish with a line that is only: {_PASTE_SENTINEL}")
        self._println("")
        lines: list[str] = []
        while True:
            try:
                line = self._readline()
            except EOFError:
                break
            if line.rstrip("\r\n") == _PASTE_SENTINEL:
                break
            lines.append(line.rstrip("\r\n"))
        return "\n".join(lines)

    def _load_txt_file(self) -> tuple[str, str] | None:
        self._println("")
        raw = self._ask("Path to .txt file: ").strip().strip('"').strip("'")
        if not raw:
            self._eprintln("error: empty path.")
            return None

        path = Path(raw).expanduser()
        if path.suffix.lower() != ".txt":
            self._eprintln("error: only .txt files are accepted.")
            return None
        if not path.is_file():
            self._eprintln(f"error: no such file: {path}")
            return None

        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            self._eprintln(f"error: could not read file: {exc}")
            return None

        self._println(f"Loaded {len(text)} characters from {path}")
        return text, str(path)

    def _ask_output_path(self) -> Path | None:
        raw = self._ask(f"Filename inside {self._output_dir}/ [{_DEFAULT_OUTPUT_NAME}]: ")
        name = raw.strip().strip('"').strip("'") or _DEFAULT_OUTPUT_NAME

        path = Path(name).expanduser()
        # Bare names always land in output/; absolute/relative paths with dirs are kept.
        if path.parent == Path("."):
            path = self._output_dir / path.name
        if path.suffix.lower() not in {".md", ".markdown"}:
            path = path.with_suffix(".md")
        return path

    def _ask(self, prompt: str) -> str:
        self._print(prompt)
        try:
            return self._readline().rstrip("\r\n")
        except EOFError:
            return ""

    def _readline(self) -> str:
        line = self._in.readline()  # type: ignore[attr-defined]
        if line == "":
            raise EOFError
        return str(line)

    def _print(self, text: str) -> None:
        self._out.write(text)  # type: ignore[attr-defined]
        self._out.flush()  # type: ignore[attr-defined]

    def _println(self, text: str = "") -> None:
        self._print(f"{text}\n")

    def _eprintln(self, text: str) -> None:
        self._err.write(f"{text}\n")  # type: ignore[attr-defined]
        self._err.flush()  # type: ignore[attr-defined]


def run_app() -> int:
    """Entry point for the interactive client."""
    return InteractiveApp().run()
