"""Tests for the interactive code-md client."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from code_md.app import InteractiveApp


def test_paste_saves_to_output_dir(tmp_path: Path) -> None:
    out_dir = tmp_path / "output"
    stdin = StringIO(
        "\n".join(
            [
                "1",
                'print("HI")',
                "END",
                "1",
                "greet",
                "",
            ]
        )
        + "\n"
    )
    stdout = StringIO()

    code = InteractiveApp(
        stdin=stdin,
        stdout=stdout,
        stderr=StringIO(),
        output_dir=out_dir,
        clipboard=lambda _t: None,
    ).run()

    assert code == 0
    saved = out_dir / "greet.md"
    assert saved.is_file()
    assert saved.read_text(encoding="utf-8").startswith("```python\n")
    assert "Saved:" in stdout.getvalue()


def test_clipboard_only(tmp_path: Path) -> None:
    clipped: list[str] = []
    stdin = StringIO(
        "\n".join(
            [
                "1",
                'print("HI")',
                "END",
                "2",
                "",
            ]
        )
        + "\n"
    )
    stdout = StringIO()

    code = InteractiveApp(
        stdin=stdin,
        stdout=stdout,
        stderr=StringIO(),
        output_dir=tmp_path / "output",
        clipboard=clipped.append,
    ).run()

    assert code == 0
    assert len(clipped) == 1
    assert clipped[0].startswith("```python\n")
    assert "Copied to clipboard." in stdout.getvalue()
    assert not (tmp_path / "output").exists() or not any((tmp_path / "output").iterdir())


def test_both_file_and_clipboard(tmp_path: Path) -> None:
    clipped: list[str] = []
    out_dir = tmp_path / "output"
    stdin = StringIO(
        "\n".join(
            [
                "1",
                "SELECT 1;",
                "END",
                "3",
                "query",
                "",
            ]
        )
        + "\n"
    )

    code = InteractiveApp(
        stdin=stdin,
        stdout=StringIO(),
        stderr=StringIO(),
        output_dir=out_dir,
        clipboard=clipped.append,
    ).run()

    assert code == 0
    assert (out_dir / "query.md").is_file()
    assert clipped and clipped[0].startswith("```sql\n")


def test_skip_delivery(tmp_path: Path) -> None:
    stdin = StringIO("1\nx = 1\nEND\n4\n")
    code = InteractiveApp(
        stdin=stdin,
        stdout=StringIO(),
        stderr=StringIO(),
        output_dir=tmp_path / "output",
        clipboard=lambda _t: None,
    ).run()
    assert code == 0


def test_load_txt_file_flow(tmp_path: Path) -> None:
    source = tmp_path / "code.txt"
    source.write_text('console.log("hi");\n', encoding="utf-8")
    stdin = StringIO(
        "\n".join(
            [
                "2",
                str(source),
                "4",
                "",
            ]
        )
        + "\n"
    )
    stdout = StringIO()

    code = InteractiveApp(
        stdin=stdin,
        stdout=stdout,
        stderr=StringIO(),
        output_dir=tmp_path / "output",
        clipboard=lambda _t: None,
    ).run()

    assert code == 0
    text = stdout.getvalue()
    assert "Detected language: javascript" in text
    assert "```javascript" in text


def test_rejects_non_txt_file(tmp_path: Path) -> None:
    source = tmp_path / "code.py"
    source.write_text("x = 1\n", encoding="utf-8")
    stdin = StringIO(f"2\n{source}\n")
    stderr = StringIO()

    code = InteractiveApp(
        stdin=stdin,
        stdout=StringIO(),
        stderr=stderr,
        output_dir=tmp_path / "output",
        clipboard=lambda _t: None,
    ).run()

    assert code == 1
    assert "only .txt files" in stderr.getvalue()


def test_quit() -> None:
    stdin = StringIO("q\n")
    stdout = StringIO()
    assert InteractiveApp(stdin=stdin, stdout=stdout, stderr=StringIO()).run() == 0
    assert "Bye." in stdout.getvalue()
