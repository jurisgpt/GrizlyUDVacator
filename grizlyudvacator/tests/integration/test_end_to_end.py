import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from grizlyudvacator.cli.io.console_io import ConsoleIO
from grizlyudvacator.cli.io.io_interface import IOInterface
from grizlyudvacator.cli.main import InterviewRunner, run_interview

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


class MockIO(IOInterface):
    """Mock IO implementation for testing."""

    def __init__(self):
        self.input_history = []
        self.output_history = []
        self.files = {}

    def read_input(self, prompt: str) -> str:
        self.output_history.append(prompt)
        return self.input_history.pop(0)

    def write_output(self, message: str) -> None:
        self.output_history.append(message)

    def read_file(self, path: str) -> str:
        return self.files.get(path, "")

    def write_file(self, path: str, content: str) -> None:
        self.files[path] = content

    def exists(self, path: str) -> bool:
        return path in self.files

    def getcwd(self) -> str:
        return os.getcwd()

    def join_path(self, *parts: str) -> str:
        return os.path.join(*parts)


def test_complete_interview_flow(tmp_path):
    """Test complete interview flow from start to document generation.

    Tests both the old and new patterns:
    1. Using InterviewRunner with explicit IO (new pattern)
    2. Using run_interview with default ConsoleIO (old pattern)
    """
    # Load test YAML
    yaml_path = os.path.join(FIXTURES_DIR, "yaml_samples", "complete_interview.yaml")
    with open(yaml_path) as f:
        yaml_content = f.read()

    # Test with InterviewRunner (new pattern)
    mock_io = MockIO()
    mock_io.files[yaml_path] = yaml_content

    user_inputs = [
        "2024-01-01",  # Date input
        "y",  # Boolean input
        "1",  # Choice input
        "test text",  # Text input
        "1,2",  # Multiple choice input
        "done",  # Multiple choice done
    ]
    mock_io.input_history = user_inputs

    runner = InterviewRunner(mock_io)
    output_path = tmp_path / "output1.docx"
    answers, flags = runner.run_interview(yaml_path, str(output_path))

    # Verify output contains expected messages
    output = "\n".join(mock_io.output_history)
    assert "📊 INTERVIEW SUMMARY" in output
    assert "🧾 Collected Answers" in output
    assert "Flags Triggered" in output

    # Verify document was generated
    assert output_path.exists()

    # Test with run_interview (old pattern)
    with patch("builtins.input", side_effect=user_inputs), patch(
        "sys.stdout", new=StringIO()
    ) as fake_out:
        yaml_data = load_yaml(yaml_path)
        output_path = tmp_path / "output2.docx"
        answers, flags = run_interview(yaml_data, str(output_path))

        # Verify output contains expected messages
        output = fake_out.getvalue()
        assert "📊 INTERVIEW SUMMARY" in output
        assert "🧾 Collected Answers" in output
        assert "Flags Triggered" in output

        # Verify document was generated
        assert output_path.exists()


def test_error_handling_in_flow(tmp_path):
    """Test error handling throughout the interview flow."""
    # Load test YAML with errors
    yaml_path = os.path.join(FIXTURES_DIR, "yaml_samples", "error_interview.yaml")
    with open(yaml_path) as f:
        yaml_content = f.read()

    # Setup mock IO
    mock_io = MockIO()
    mock_io.files[yaml_path] = yaml_content

    # Mock user inputs
    user_inputs = [
        "invalid date",  # Invalid date input
        "x",  # Invalid boolean input
        "0",  # Invalid choice input
        "",  # Empty text input
        "a,b",  # Invalid multiple choice input
        "done",  # Multiple choice done
    ]
    mock_io.input_history = user_inputs

    # Create interview runner
    runner = InterviewRunner(mock_io)

    # Run interview
    output_path = tmp_path / "output.docx"
    answers, flags = runner.run_interview(yaml_path, str(output_path))

    # Verify error messages are shown
    output = "\n".join(mock_io.output_history)
    assert "Invalid date format" in output
    assert "Please enter y or n" in output
    assert "Invalid choice" in output
    assert "Invalid input" in output
    assert "Interview complete" in output


def test_document_generation(tmp_path):
    """Test document generation at the end of interview."""
    # Load test YAML
    yaml_path = os.path.join(FIXTURES_DIR, "yaml_samples", "document_interview.yaml")
    with open(yaml_path) as f:
        yaml_content = f.read()

    # Setup mock IO
    mock_io = MockIO()
    mock_io.files[yaml_path] = yaml_content

    # Mock user inputs
    user_inputs = ["2024-01-01"] * 10
    mock_io.input_history = user_inputs

    # Create interview runner
    runner = InterviewRunner(mock_io)

    # Run interview
    output_path = tmp_path / "output.docx"
    answers, flags = runner.run_interview(yaml_path, str(output_path))

    # Verify document was created
    assert output_path.exists()
    assert "Document generated successfully" in "\n".join(mock_io.output_history)


def test_permission_denied_handling(tmp_path):
    """Test handling of permission denied errors."""
    # Load test YAML
    yaml_path = os.path.join(FIXTURES_DIR, "yaml_samples", "complete_interview.yaml")
    with open(yaml_path) as f:
        yaml_content = f.read()

    # Setup mock IO that raises PermissionError
    class MockIOWithError(MockIO):
        def write_file(self, path: str, content: str) -> None:
            raise PermissionError("Permission denied")

    mock_io = MockIOWithError()
    mock_io.files[yaml_path] = yaml_content

    # Create interview runner
    runner = InterviewRunner(mock_io)

    # Run interview
    output_path = tmp_path / "output.docx"
    with pytest.raises(SystemExit):
        runner.run_interview(yaml_path, str(output_path))

    # Verify error message was shown
    output = "\n".join(mock_io.output_history)
    assert "Permission denied" in output
