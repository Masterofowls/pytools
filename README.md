# code-md

Interactive client that turns code into markdown fenced snippets with automatic
language detection and normalized indentation.

## Install

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -U pip
pip install -e .
```

For development (tests, lint, types):

```bash
pip install -r requirements-dev.txt
```

## Usage

### Interactive client (default)

```bash
code-md
```

The app asks how you want to provide code:

1. **Paste inline text** — paste your code, then type `END` on its own line
2. **Load a .txt file** — enter the path to a `.txt` file

It detects the language, prints the markdown fence, then asks:

1. **Save .md** under `output/`
2. **Copy to clipboard**
3. **Both**
4. **Skip** (screen only)

```text
================================================
  code-md  ·  Markdown code-snippet client
================================================

How do you want to provide the code?
  [1] Paste inline text
  [2] Load a .txt file
  [q] Quit
```

Force interactive mode even when stdin is piped:

```bash
code-md -i
```

### Library

```python
from code_md import to_markdown

print(to_markdown('print("HI")'))
```

### Non-interactive CLI

```bash
# From stdin
echo 'print("HI")' | code-md

# From a file
code-md src\code_md\fence.py -o snippet.md
```

## Features

- Interactive prompt: paste text or load `.txt`
- Auto-detects language via heuristics + Pygments
- Dedents shared leading whitespace while keeping relative indentation
- Save to `output/*.md`, copy to clipboard, or both
- Non-interactive file/stdin mode still available

## Development

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
black --check .
mypy src
```
