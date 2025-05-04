import os
from typing import Any, Optional

from grizlyudvacator.cli.io.io_interface import IOInterface


class ConsoleIO(IOInterface):
    """Concrete implementation of IOInterface for console I/O."""

    def read_input(self, prompt: str) -> str:
        """Read input from user via console."""
        return input(prompt)

    def write_output(self, message: str) -> None:
        """Write output to console."""
        print(message)

    def read_file(self, path: str) -> Any:
        """Read file contents using built-in open."""
        with open(path) as f:
            return f.read()

    def write_file(self, path: str, content: Any) -> None:
        """Write content to file using built-in open."""
        with open(path, "w") as f:
            f.write(content)

    def exists(self, path: str) -> bool:
        """Check if file exists using os.path."""
        return os.path.exists(path)

    def getcwd(self) -> str:
        """Get current working directory using os."""
        return os.getcwd()

    def join_path(self, *parts: str) -> str:
        """Join path components using os.path."""
        return os.path.join(*parts)
