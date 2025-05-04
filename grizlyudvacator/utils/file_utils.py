import os
from pathlib import Path
from typing import Optional


def safe_write_file(path: Path, content: str) -> None:
    """Write content to a file, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def get_file_extension(path: str) -> str:
    """Get the file extension from a path."""
    return Path(path).suffix.lower()


def ensure_directory_exists(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)


def get_file_size(path: Path) -> int | None:
    """Get the size of a file in bytes, or None if file doesn't exist."""
    if path.exists():
        return path.stat().st_size
    return None
