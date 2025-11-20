# 🦴 Rigby - The Code Raccoon 🦝

Rigby parses Python code and extracts its skeletal structure into **TOON format**. It's useful for feeding code context to LLMs without using too many tokens, or for quickly understanding the high-level architecture of a project.

## Features

- **AST Parsing**: Uses Python's native `ast` module (safe, no execution).
- **TOON Format**: A concise representation of:
    - Classes (`CLS`) & Inheritance
    - Functions (`FUNC`) & Async Functions (`ASYNC_FUNC`)
    - Methods (`MTHD`) & Async Methods (`ASYNC_MTHD`)
    - Global Variables (`VAR`)
    - Docstrings (flattened & truncated)
- **Robust**: Handles complex type hints, decorators, and directory recursion.

## Installation

You can install Rigby using `pip` or `uv`.

### Using `uv` (Recommended)

```bash
uv pip install rigby-toon
```

### Using `pip`

```bash
pip install rigby-toon
```

## Usage

### Command Line

Run Rigby against a file or a directory:

```bash
# Parse a single file
rigby parse my_script.py

# Parse an entire directory recursively
rigby parse ./my_project/
```

**Output Example (TOON Format):**

```text
CLS Dog(Animal):
  MTHD __init__(self, name:str): "Initializes a dog."
  MTHD bark(self) -> None: "Makes noise."

FUNC main():
```

### Python API

You can also use Rigby in your own scripts:

```python
from rigby import parse_file, process_path

# Get TOON string for a single file
toon_context, item_count = parse_file("path/to/file.py")
print(toon_context)

# Process directory (prints to stdout)
process_path("path/to/project")
```

## Development

This project is managed with [uv](https://github.com/astral-sh/uv).

1. **Clone the repo:**
   ```bash
   git clone https://github.com/yourusername/rigby.git
   cd rigby
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Run Tests:**
   ```bash
   uv run pytest
   ```

4. **Lint & Format:**
   ```bash
   uv run ruff check .
   uv run ruff format .
   ```

## Publishing

To publish to PyPI (requires `uv`):

```bash
uv build
uv publish
```

## License

MIT
