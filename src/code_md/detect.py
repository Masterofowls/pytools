"""Automatic source-language detection for markdown fences."""

from __future__ import annotations

import re
from typing import Final

from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound

# Map Pygments aliases / names → common markdown fence tags.
_ALIAS_TO_FENCE: Final[dict[str, str]] = {
    "python": "python",
    "py": "python",
    "python3": "python",
    "javascript": "javascript",
    "js": "javascript",
    "nodejs": "javascript",
    "typescript": "typescript",
    "ts": "typescript",
    "tsx": "tsx",
    "jsx": "jsx",
    "bash": "bash",
    "shell": "bash",
    "sh": "bash",
    "zsh": "bash",
    "console": "bash",
    "powershell": "powershell",
    "pwsh": "powershell",
    "ps1": "powershell",
    "html": "html",
    "xml": "xml",
    "css": "css",
    "scss": "scss",
    "json": "json",
    "yaml": "yaml",
    "yml": "yaml",
    "toml": "toml",
    "ini": "ini",
    "sql": "sql",
    "rust": "rust",
    "go": "go",
    "golang": "go",
    "java": "java",
    "c": "c",
    "cpp": "cpp",
    "c++": "cpp",
    "csharp": "csharp",
    "c#": "csharp",
    "cs": "csharp",
    "ruby": "ruby",
    "rb": "ruby",
    "php": "php",
    "swift": "swift",
    "kotlin": "kotlin",
    "r": "r",
    "markdown": "markdown",
    "md": "markdown",
    "dockerfile": "dockerfile",
    "docker": "dockerfile",
    "text": "text",
    "plain": "text",
}

_HEURISTICS: Final[list[tuple[re.Pattern[str], str]]] = [
    (re.compile(r"^\s*#!.*\bpython", re.I | re.M), "python"),
    (re.compile(r"^\s*#!.*\b(ba)?sh\b", re.I | re.M), "bash"),
    (re.compile(r"^\s*#!.*\b(pwsh|powershell)\b", re.I | re.M), "powershell"),
    (re.compile(r"^\s*from\s+\w+\s+import\s+|^\s*import\s+\w+", re.M), "python"),
    (re.compile(r"^\s*def\s+\w+\s*\(|^\s*async\s+def\s+\w+\s*\(", re.M), "python"),
    (re.compile(r'^\s*print\s*\(|^\s*if\s+__name__\s*==\s*[\'"]__main__', re.M), "python"),
    (re.compile(r"^\s*(const|let|var)\s+\w+\s*=", re.M), "javascript"),
    (re.compile(r"^\s*(export\s+)?(async\s+)?function\s+\w+", re.M), "javascript"),
    (re.compile(r"^\s*console\.(log|error|warn)\s*\(", re.M), "javascript"),
    (re.compile(r":\s*(string|number|boolean|void)\b|interface\s+\w+", re.M), "typescript"),
    (re.compile(r"^\s*fn\s+\w+|^\s*use\s+\w+::|^\s*pub\s+(fn|struct|enum)", re.M), "rust"),
    (re.compile(r"^\s*package\s+main\b|^\s*func\s+\w+\s*\(", re.M), "go"),
    (re.compile(r"^\s*public\s+class\s+\w+|^\s*System\.out\.println", re.M), "java"),
    (re.compile(r"^\s*#include\s*<|^\s*int\s+main\s*\(", re.M), "c"),
    (re.compile(r"^\s*SELECT\b|^\s*INSERT\s+INTO\b|^\s*CREATE\s+TABLE\b", re.I | re.M), "sql"),
    (re.compile(r"^\s*\{\s*[\n\r]|^\s*\"[^\"]+\"\s*:\s*", re.M), "json"),
    (re.compile(r"^\s*---\s*$|^\s*\w+:\s+.+$", re.M), "yaml"),
    (re.compile(r"^\s*\[.+\]\s*$|^\s*\w+\s*=\s*.+$", re.M), "toml"),
    (re.compile(r"^\s*<(!DOCTYPE|html|div|span|body)\b", re.I | re.M), "html"),
    (re.compile(r"^\s*(FROM|RUN|COPY|WORKDIR|CMD|ENTRYPOINT)\b", re.M), "dockerfile"),
    (re.compile(r"^\s*\$\w+\s*=|^\s*Write-Host\b|^\s*Get-\w+", re.M), "powershell"),
]


def _normalize_alias(alias: str) -> str:
    key = alias.strip().lower()
    return _ALIAS_TO_FENCE.get(key, key.replace(" ", "-"))


def detect_language(code: str, *, filename: str | None = None) -> str:
    """Detect a markdown fence language tag for *code*.

    Prefers filename extension hints, then heuristics, then Pygments.
    Falls back to ``text`` when nothing matches.
    """
    if filename:
        from pathlib import Path

        suffix = Path(filename).suffix.lstrip(".").lower()
        if suffix in _ALIAS_TO_FENCE:
            return _ALIAS_TO_FENCE[suffix]

    stripped = code.strip()
    if not stripped:
        return "text"

    for pattern, lang in _HEURISTICS:
        if pattern.search(stripped):
            return lang

    try:
        lexer = guess_lexer(stripped)
        aliases = getattr(lexer, "aliases", None) or []
        if aliases:
            return _normalize_alias(aliases[0])
        name = getattr(lexer, "name", "") or ""
        if name:
            return _normalize_alias(name)
    except ClassNotFound:
        pass

    return "text"
