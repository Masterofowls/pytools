"""Automatic source-language detection for markdown fences."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

# Extension / alias → common markdown fence tags.
_ALIAS_TO_FENCE: Final[dict[str, str]] = {
    "python": "python",
    "py": "python",
    "pyw": "python",
    "python3": "python",
    "javascript": "javascript",
    "js": "javascript",
    "mjs": "javascript",
    "cjs": "javascript",
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
    "htm": "html",
    "xml": "xml",
    "css": "css",
    "scss": "scss",
    "json": "json",
    "yaml": "yaml",
    "yml": "yaml",
    "toml": "toml",
    "ini": "ini",
    "cfg": "ini",
    "conf": "ini",
    "sql": "sql",
    "rust": "rust",
    "rs": "rust",
    "go": "go",
    "golang": "go",
    "java": "java",
    "c": "c",
    "h": "c",
    "cpp": "cpp",
    "cc": "cpp",
    "cxx": "cpp",
    "hpp": "cpp",
    "c++": "cpp",
    "csharp": "csharp",
    "c#": "csharp",
    "cs": "csharp",
    "ruby": "ruby",
    "rb": "ruby",
    "php": "php",
    "swift": "swift",
    "kotlin": "kotlin",
    "kt": "kotlin",
    "r": "r",
    "markdown": "markdown",
    "md": "markdown",
    "dockerfile": "dockerfile",
    "docker": "dockerfile",
    "text": "text",
    "txt": "text",
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


_GENERIC_EXTENSIONS: Final[frozenset[str]] = frozenset({"txt", "text", "plain"})


def detect_language(code: str, *, filename: str | None = None) -> str:
    """Detect a markdown fence language tag for *code*.

    Prefers filename extension hints (except generic ones like ``.txt``),
    then regex heuristics. Falls back to ``text`` when nothing matches.
    """
    if filename:
        suffix = Path(filename).suffix.lstrip(".").lower()
        if suffix and suffix not in _GENERIC_EXTENSIONS and suffix in _ALIAS_TO_FENCE:
            return _ALIAS_TO_FENCE[suffix]

    stripped = code.strip()
    if not stripped:
        return "text"

    for pattern, lang in _HEURISTICS:
        if pattern.search(stripped):
            return lang

    return "text"