"""CLI tests for code-md."""

from __future__ import annotations

from pathlib import Path

from code_md.cli import main


def test_missing_file_exits_cleanly(capsys) -> None:
    assert main(["does-not-exist.py"]) == 1
    err = capsys.readouterr().err
    assert "No such file: does-not-exist.py" in err
    assert "stdin" in err.lower()


def test_reads_existing_file(tmp_path: Path, capsys) -> None:
    source = tmp_path / "sample.py"
    source.write_text('print("HI")\n', encoding="utf-8")
    assert main([str(source)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("```python\n")
    assert 'print("HI")' in out
