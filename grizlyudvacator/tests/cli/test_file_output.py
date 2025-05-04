from unittest.mock import MagicMock, patch

import pytest

from grizlyudvacator.cli.io.console_io import ConsoleIO
from grizlyudvacator.cli.io.io_interface import IOInterface
from grizlyudvacator.cli.main import save_results


@pytest.fixture
def test_io():
    class TestIO(IOInterface):
        def __init__(self):
            self.files = {}
            self.output = []

        def read_input(self, prompt: str) -> str:
            return ""

        def write_output(self, message: str) -> None:
            self.output.append(message)

        def read_file(self, path: str) -> str:
            return self.files.get(path, "")

        def write_file(self, path: str, content: str) -> None:
            self.files[path] = content

        def exists(self, path: str) -> bool:
            return path in self.files

        def getcwd(self) -> str:
            return ""

        def join_path(self, *parts: str) -> str:
            return "/".join(parts)

    return TestIO()


def test_save_results_basic(test_io):
    """Test saving basic results."""
    io = test_io
    answers = {"q1": "answer1", "q2": "answer2"}
    flags = ["flag1", "flag2"]

    result = save_results(answers, flags, "test.txt", io)
    assert result is True

    # Verify file content
    content = io.files["test.txt"]
    assert "📊 INTERVIEW RESULTS" in content
    assert "🧾 Collected Answers:" in content
    assert "- q1: answer1" in content
    assert "- q2: answer2" in content
    assert "🚩 Flags Triggered:" in content
    assert "- flag1" in content
    assert "- flag2" in content

    # Verify success message
    assert "💾 Results saved to: test.txt" in "\n".join(io.output)


def test_save_results_with_list_answer():
    """Test saving results with list answers."""
    io = TestIO()
    answers = {"q1": ["item1", "item2", "item3"]}
    flags = []

    result = save_results(answers, flags, "test.txt", io)
    assert result is True

    content = io.files["test.txt"]
    assert "- q1:" in content
    assert "  * item1" in content
    assert "  * item2" in content
    assert "  * item3" in content


def test_save_results_with_invalid_path():
    """Test saving results with invalid path."""
    io = TestIO()

    # Mock write_file to raise PermissionError
    def mock_write_file(path, content):
        raise PermissionError("Permission denied")

    io.write_file = mock_write_file

    answers = {"q1": "answer1"}
    flags = []

    result = save_results(answers, flags, "test.txt", io)
    assert result is False

    # Verify error message
    assert "❌ Failed to save results" in "\n".join(io.output)


def test_save_results_with_auto_filename():
    """Test saving results with auto-generated filename."""
    io = TestIO()
    answers = {"q1": "answer1"}
    flags = []

    result = save_results(answers, flags, None, io)
    assert result is True

    # Verify file was created with timestamp
    assert len(io.files) == 1
    filename = list(io.files.keys())[0]
    assert filename.startswith("interview_results_")
    assert filename.endswith(".txt")


def test_save_results_with_empty_data():
    """Test saving results with empty data."""
    io = TestIO()

    result = save_results({}, [], "test.txt", io)
    assert result is True

    content = io.files["test.txt"]
    assert "📊 INTERVIEW RESULTS" in content
    assert "🧾 Collected Answers:" in content
    assert "No answers collected" in content
    assert "No flags triggered" in content
