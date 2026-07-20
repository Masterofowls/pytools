"""CLI and interactive client entry for code-md."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from code_md.app import run_app
from code_md.fence import to_markdown


def _read_input(path: Path | None) -> tuple[str, str | None]:
    if path is None or str(path) == "-":
        return sys.stdin.read(), None
    if not path.is_file():
        raise FileNotFoundError(
            f"No such file: {path}\n"
            "Pass an existing source file, run `code-md` with no args for the "
            "interactive client, or pipe code via stdin."
        )
    text = path.read_text(encoding="utf-8")
    return text, str(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code-md",
        description=(
            "Interactive markdown code-snippet client. "
            "With no arguments, asks whether to paste text or load a .txt file. "
            "You can also pass a file path or pipe stdin for non-interactive use."
        ),
    )
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        help="Optional input file (skips interactive mode).",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Force the interactive client.",
    )
    parser.add_argument(
        "-l",
        "--language",
        help="Force fence language (non-interactive only).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write markdown to this file (non-interactive only).",
    )
    parser.add_argument(
        "--no-blank-line",
        action="store_true",
        help="Do not insert a blank line after the opening fence.",
    )
    return parser


def _should_run_interactive(args: argparse.Namespace) -> bool:
    if args.interactive:
        return True
    if args.source is not None or args.language or args.output:
        return False
    # No CLI args: interactive when attached to a terminal; else read stdin pipe.
    return sys.stdin.isatty()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if _should_run_interactive(args):
        return run_app()

    try:
        code, filename = _read_input(args.source)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    markdown = to_markdown(
        code,
        language=args.language,
        filename=filename,
        blank_line_after_fence=not args.no_blank_line,
    )

    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
    else:
        sys.stdout.write(markdown)

    return 0
