import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from grizlyudvacator.cli.io.console_io import ConsoleIO
from grizlyudvacator.cli.io.io_interface import IOInterface
from grizlyudvacator.cli.main import InterviewRunner, load_yaml, run_interview
from grizlyudvacator.utils.file_utils import safe_write_file
from grizlyudvacator.utils.path_utils import get_fixture_dir

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class MockIO:
    def __init__(self):
        self.responses = {}
        self.questions_asked = []
        self.files_written = []
        self.files = {}

    def write_output(self, text):
        self.questions_asked.append(text)

    def read_input(self, prompt):
        # Extract question ID from prompt
        question_id = prompt.split(" ")[-1].rstrip(":")
        return self.responses.get(question_id, "")

    def write_file(self, path: str, content: str):
        """Write content to a file, tracking the operation."""
        path = Path(path)
        self.files_written.append(str(path))
        self.files[str(path)] = content
        safe_write_file(path, content)

    def get_files_written(self):
        return self.files

    def get_questions_asked(self):
        return self.questions_asked


# Test data
FIXTURES_DIR = get_fixture_dir()

# Load test data
with open(FIXTURES_DIR / "test_questions.yaml") as f:
    TEST_QUESTIONS = yaml.safe_load(f)

with open(FIXTURES_DIR / "test_answers.yaml") as f:
    TEST_ANSWERS = yaml.safe_load(f)

with open(FIXTURES_DIR / "test_flags.yaml") as f:
    TEST_FLAGS = yaml.safe_load(f)


@pytest.fixture
def mock_io():
    return MockIO()


@pytest.fixture
def test_yaml_path():
    return str(FIXTURES_DIR / "test_questions.yaml")


def test_interview_with_followup_questions(mock_io, test_yaml_path):
    """Test interview with followup questions."""
    # Setup mock inputs for followup flow
    mock_io.responses = {"followup_question": "followup answer", "end_question": "n"}

    # Run interview
    runner = InterviewRunner(yaml_path=test_yaml_path, io=mock_io)
    results = runner.run()

    # Verify results
    assert len(mock_io.questions_asked) > 0
    assert len(mock_io.files_written) == 0  # No files should be written
    assert results == TEST_ANSWERS


def test_interview_with_flags(mock_io, test_yaml_path):
    """Test interview that triggers flags."""
    # Setup mock inputs
    mock_io.responses = {"flag_question": "y", "end_question": "n"}

    # Load YAML with flag questions
    with open(test_yaml_path) as f:
        yaml_content = f.read()
    mock_io.files[test_yaml_path] = yaml_content
    mock_io.files[test_yaml_path] = yaml_content

    # Run interview
    runner = InterviewRunner(mock_io)
    answers, flags = runner.run_interview(test_yaml_path)

    # Verify flags were set
    assert "old_date" in flags
    assert "future_date" in flags
    assert "recent_date" in flags


def test_interview_with_invalid_inputs(mock_io, test_yaml_path):
    """Test handling of invalid inputs."""
    # Setup mock inputs with invalid values
    mock_io.input_history = [
        "invalid",  # Invalid boolean
        "y",  # Correct boolean
        "invalid",  # Invalid date
        "2024-01-01",  # Correct date
        "invalid",  # Invalid choice
        "1",  # Correct choice
    ]

    # Load YAML
    with open(test_yaml_path) as f:
        yaml_content = f.read()
    mock_io.files[test_yaml_path] = yaml_content

    # Run interview
    runner = InterviewRunner(mock_io)
    answers, flags = runner.run_interview(test_yaml_path)

    # Verify error messages
    output = "\n".join(mock_io.output_history)
    assert "Invalid input" in output
    assert "Please enter a valid date" in output
    assert "Please select a valid option" in output


def test_interview_with_missing_required_fields(mock_io, test_yaml_path):
    """Test handling of missing required fields."""
    # Setup mock inputs
    mock_io.input_history = [
        "",  # Empty required field
        "test",  # Valid input
        "y",  # End interview
    ]

    # Load YAML with required fields
    with open(test_yaml_path) as f:
        yaml_content = f.read()
    mock_io.files[test_yaml_path] = yaml_content

    # Run interview
    runner = InterviewRunner(mock_io)
    answers, flags = runner.run_interview(test_yaml_path)

    # Verify error message
    output = "\n".join(mock_io.output_history)
    assert "This field is required" in output


def test_interview_with_conditional_logic(mock_io, test_yaml_path):
    """Test conditional question logic."""
    # Setup mock inputs for conditional paths
    mock_io.input_history = [
        "y",  # Trigger conditional path
        "conditional answer",  # Answer conditional question
        "n",  # Skip conditional path
        "main answer",  # Answer main path
    ]

    # Load YAML with conditional questions
    with open(test_yaml_path) as f:
        yaml_content = f.read()
    mock_io.files[test_yaml_path] = yaml_content

    # Run interview
    runner = InterviewRunner(mock_io)
    answers, flags = runner.run_interview(test_yaml_path)

    # Verify conditional questions were asked correctly
    output = "\n".join(mock_io.output_history)
    assert "Conditional question:" in output
    assert "conditional answer" in answers
    assert "main answer" in answers


def test_interview_with_multiple_flags(mock_io, test_yaml_path):
    """Test multiple flag conditions."""
    # Setup mock inputs to trigger multiple flags
    mock_io.input_history = [
        "2022-01-01",  # Old date
        "2025-01-01",  # Future date
        "y",  # Boolean flag
        "option1",  # Choice flag
    ]

    # Load YAML with multiple flag conditions
    with open(test_yaml_path) as f:
        yaml_content = f.read()
    mock_io.files[test_yaml_path] = yaml_content

    # Run interview
    runner = InterviewRunner(mock_io)
    answers, flags = runner.run_interview(test_yaml_path)

    # Verify multiple flags were set
    assert "old_date" in flags
    assert "future_date" in flags
    assert "boolean_flag" in flags
    assert "choice_flag" in flags


def test_interview_with_validation_rules(mock_io, test_yaml_path):
    """Test input validation rules."""
    # Setup mock inputs with invalid values
    mock_io.input_history = [
        "invalid",  # Invalid email
        "test@example.com",  # Valid email
        "123",  # Invalid phone
        "555-123-4567",  # Valid phone
        "abc",  # Invalid SSN
        "123-45-6789",  # Valid SSN
    ]

    # Load YAML with validation rules
    with open(test_yaml_path) as f:
        yaml_content = f.read()
    mock_io.files[test_yaml_path] = yaml_content

    # Run interview
    runner = InterviewRunner(mock_io)
    answers, flags = runner.run_interview(test_yaml_path)

    # Verify validation messages
    output = "\n".join(mock_io.output_history)
    assert "Invalid email format" in output
    assert "Invalid phone number format" in output
    assert "Invalid SSN format" in output


def test_interview_with_default_values(mock_io, test_yaml_path):
    """Test default values for questions."""
    # Setup mock inputs with empty values
    mock_io.input_history = [
        "",  # Empty input, should use default
        "test",  # Override default
        "",  # Empty input, should use default
    ]

    # Load YAML with default values
    with open(test_yaml_path) as f:
        yaml_content = f.read()
    mock_io.files[test_yaml_path] = yaml_content

    # Run interview
    runner = InterviewRunner(mock_io)
    answers, flags = runner.run_interview(test_yaml_path)

    # Verify default values were used
    assert answers["default_question"] == "default_value"
    assert answers["override_question"] == "test"
    assert answers["another_default"] == "another_default_value"


def test_interview_with_dynamic_questions(mock_io, test_yaml_path):
    """Test dynamic question generation based on previous answers."""
    # Setup mock inputs for dynamic questions
    mock_io.input_history = [
        "y",  # Trigger dynamic questions
        "dynamic answer 1",  # First dynamic question
        "dynamic answer 2",  # Second dynamic question
        "n",  # Skip dynamic questions
        "main answer",  # Main path question
    ]

    # Load YAML with dynamic questions
    with open(test_yaml_path) as f:
        yaml_content = f.read()
    mock_io.files[test_yaml_path] = yaml_content

    # Run interview
    runner = InterviewRunner(mock_io)
    answers, flags = runner.run_interview(test_yaml_path)

    # Verify dynamic questions were asked
    output = "\n".join(mock_io.output_history)
    assert "Dynamic question 1:" in output
    assert "Dynamic question 2:" in output
    assert "dynamic answer 1" in answers
    assert "dynamic answer 2" in answers
    assert "main answer" in answers
