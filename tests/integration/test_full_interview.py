from unittest.mock import MagicMock, patch

import pytest

from grizlyudvacator.cli.io.console_io import ConsoleIO
from grizlyudvacator.cli.main import (
    _ask_question_impl as ask_question,
    _run_interview_impl,
    load_yaml,
)


def test_full_interview_flow():
    """Test complete interview flow with mock user input."""
    # Create mock IO interface
    mock_io = ConsoleIO()
    mock_io.write_output = MagicMock()
    mock_io.read_input = MagicMock(side_effect=["n", "y"])  # Simulate user input

    # Create mock YAML data
    yaml_data = {
        "questions": [
            {
                "id": "intro",
                "prompt": "Did you respond to the court papers?",
                "type": "boolean",
                "follow_up": {
                    "if_true": {"flags": ["responded"], "next": "end"},
                    "if_false": {"flags": ["no_response"], "next": "end"},
                },
            },
            {"id": "end", "type": "summary"},
        ]
    }

    # Run the interview
    answers, flags = _run_interview_impl(mock_io, yaml_data)

    # Verify output prompts
    mock_io.write_output.assert_any_call("\n❓ Did you respond to the court papers?")
    mock_io.write_output.assert_any_call("Enter [y/n]: ")
    mock_io.write_output.assert_any_call("Enter [y/n]: ")
    mock_io.write_output.assert_any_call("\n" + "=" * 50)
    mock_io.write_output.assert_any_call("📊 INTERVIEW SUMMARY")
    mock_io.write_output.assert_any_call("=" * 50)
    mock_io.write_output.assert_any_call("\n🧾 Collected Answers:")
    mock_io.write_output.assert_any_call(" - intro: False")
    mock_io.write_output.assert_any_call("\n🚩 Flags Triggered:")
    mock_io.write_output.assert_any_call(" - no_response")

    # Verify results
    assert answers == {"intro": False}
    assert flags == ["no_response"]


def test_interview_with_multiple_questions():
    """Test interview with multiple questions and different types."""
    mock_io = ConsoleIO()
    mock_io.write_output = MagicMock()
    mock_io.read_input = MagicMock(side_effect=["y", "2", "2025-05-01", "1,3,done"])

    yaml_data = {
        "questions": [
            {"id": "boolean_q", "prompt": "Is this a test?", "type": "boolean"},
            {
                "id": "choice_q",
                "prompt": "Choose an option:",
                "type": "choice",
                "options": ["Option 1", "Option 2", "Option 3"],
            },
            {"id": "date_q", "prompt": "When is the deadline?", "type": "date"},
            {
                "id": "multiple_choice_q",
                "prompt": "Select multiple options:",
                "type": "multiple_choice",
                "options": ["Option A", "Option B", "Option C"],
            },
            {"id": "end", "type": "summary"},
        ]
    }

    answers, flags = _run_interview_impl(mock_io, yaml_data)

    assert answers == {
        "boolean_q": True,
        "choice_q": "Option 2",
        "date_q": "2025-05-01",
        "multiple_choice_q": ["Option B", "Option C"],
    }
    assert flags == []


def test_interview_with_invalid_input_handling():
    """Test how the interview handles invalid user input."""
    mock_io = ConsoleIO()
    mock_io.write_output = MagicMock()
    mock_io.read_input = MagicMock(
        side_effect=["invalid", "y", "abc", "1", "2025-05-01", "invalid", "1,2,done"]
    )

    yaml_data = {
        "questions": [
            {"id": "boolean_q", "prompt": "Is this a test?", "type": "boolean"},
            {
                "id": "choice_q",
                "prompt": "Choose an option:",
                "type": "choice",
                "options": ["Option 1", "Option 2"],
            },
            {"id": "date_q", "prompt": "When is the deadline?", "type": "date"},
            {
                "id": "multiple_choice_q",
                "prompt": "Select multiple options:",
                "type": "multiple_choice",
                "options": ["Option A", "Option B", "Option C"],
            },
            {"id": "end", "type": "summary"},
        ]
    }

    answers, flags = _run_interview_impl(mock_io, yaml_data)

    assert answers == {
        "boolean_q": True,
        "choice_q": "Option 1",
        "date_q": "2025-05-01",
        "multiple_choice_q": ["Option A", "Option B"],
    }
    assert flags == []

    # Verify error messages were shown
    mock_io.write_output.assert_any_call("Please enter y or n.")
    mock_io.write_output.assert_any_call("Invalid choice.")
    mock_io.write_output.assert_any_call("Invalid date format. Please use YYYY-MM-DD.")
    mock_io.write_output.assert_any_call(
        "Invalid input. Enter numbers separated by commas."
    )
