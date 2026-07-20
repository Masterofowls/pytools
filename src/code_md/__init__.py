"""code-md — wrap source in markdown fences with auto language detection."""

from code_md.cli import main
from code_md.detect import detect_language
from code_md.fence import normalize_indentation, to_markdown

__all__ = [
    "detect_language",
    "main",
    "normalize_indentation",
    "to_markdown",
]

__version__ = "0.1.0"
