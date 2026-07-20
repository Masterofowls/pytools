"""Convert source code into markdown fenced code blocks."""

from __future__ import annotations

import textwrap

from code_md.detect import detect_language


def _fence_marker(code: str) -> str:
    """Return a backtick run longer than any run inside *code* (CommonMark)."""
    longest = 0
    current = 0
    for char in code:
        if char == "`":
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    length = max(3, longest + 1)
    return "`" * length


def normalize_indentation(code: str) -> str:
    """Dedent shared leading whitespace and trim trailing blank lines.

    Relative indentation between lines is preserved. Leading/trailing blank
    lines around the block are removed so the fence body stays clean.
    """
    if not code:
        return ""

    # Expand tabs so indentation is stable across editors.
    expanded = code.expandtabs(4)
    dedented = textwrap.dedent(expanded)
    lines = dedented.splitlines()

    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    return "\n".join(lines)


def to_markdown(
    code: str,
    *,
    language: str | None = None,
    filename: str | None = None,
    blank_line_after_fence: bool = True,
) -> str:
    """Wrap *code* in a markdown fenced code block.

    Parameters
    ----------
    code:
        Raw source text.
    language:
        Explicit fence language. When omitted, language is auto-detected.
    filename:
        Optional path hint used during detection (extension-based).
    blank_line_after_fence:
        When True, insert a blank line after the opening fence (matches the
        common snippet style from the project brief).
    """
    body = normalize_indentation(code)
    lang = (language or detect_language(body, filename=filename)).strip() or "text"
    fence = _fence_marker(body)

    opener = f"{fence}{lang}"
    if blank_line_after_fence:
        return f"{opener}\n\n{body}\n\n{fence}\n"
    return f"{opener}\n{body}\n{fence}\n"
