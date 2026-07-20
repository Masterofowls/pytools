# Contributing

1. Use **pip** + a project virtualenv (`.venv`) for dependencies.
2. Runtime code must stay **stdlib-only** (no new third-party runtime deps).
3. Conventional commits: `feat:`, `fix:`, `chore:`, `refactor:`, `docs:`, `test:`.
4. Before opening a PR, run:

```bash
pip install -r requirements-dev.txt
ruff check .
black .
mypy src
pytest
```

5. Keep modules focused; avoid files over ~1000 lines.
6. Append a short note to `docs/ACTIVITY_LOG.md` for meaningful changes.
