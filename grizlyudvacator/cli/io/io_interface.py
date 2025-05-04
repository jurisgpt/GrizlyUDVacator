from abc import ABC, abstractmethod
from typing import Any, Optional


class IOInterface(ABC):
    """Interface for input/output operations."""

    @abstractmethod
    def read_input(self, prompt: str) -> str:
        """Read input from user."""
        pass

    @abstractmethod
    def write_output(self, message: str) -> None:
        """Write output to user."""
        pass

    @abstractmethod
    def read_file(self, path: str) -> Any:
        """Read file contents."""
        pass

    @abstractmethod
    def write_file(self, path: str, content: Any) -> None:
        """Write content to file."""
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if file exists."""
        pass

    @abstractmethod
    def getcwd(self) -> str:
        """Get current working directory."""
        pass

    @abstractmethod
    def join_path(self, *parts: str) -> str:
        """Join path components."""
        pass
