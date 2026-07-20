"""Tests for code-md language detection and markdown fencing."""

from __future__ import annotations

from code_md import detect_language, normalize_indentation, to_markdown


def test_python_snippet_matches_expected_shape() -> None:
    result = to_markdown('print("HI")')
    assert result == '```python\n\nprint("HI")\n\n```\n'


def test_preserves_relative_indentation() -> None:
    code = """\
    def greet(name):
        print(f"hi {name}")
            # deeper
"""
    result = to_markdown(code)
    assert "```python\n\n" in result
    assert 'def greet(name):\n    print(f"hi {name}")\n        # deeper' in result


def test_detect_javascript() -> None:
    assert detect_language('console.log("hi");') == "javascript"


def test_detect_from_filename() -> None:
    assert detect_language("x = 1", filename="app.ts") == "typescript"


def test_force_language() -> None:
    result = to_markdown("SELECT 1;", language="sql")
    assert result.startswith("```sql\n")


def test_nested_backticks_extend_fence() -> None:
    code = "x = ```inner```"
    result = to_markdown(code, language="text", blank_line_after_fence=False)
    assert result.startswith("````text\n")
    assert result.endswith("````\n")


def test_normalize_indentation_strips_common_indent() -> None:
    code = "    a\n        b\n    c\n"
    assert normalize_indentation(code) == "a\n    b\nc"


def test_empty_code() -> None:
    assert to_markdown("", language="text") == "```text\n\n\n\n```\n"
