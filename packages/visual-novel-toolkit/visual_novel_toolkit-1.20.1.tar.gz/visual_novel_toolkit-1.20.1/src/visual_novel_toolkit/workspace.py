from pathlib import Path
from typing import Final


internal_directory: Final = Path(".vntk")


def workspace() -> Path:
    internal_directory.mkdir(exist_ok=True)
    (internal_directory / ".gitignore").write_text("*")
    return internal_directory
