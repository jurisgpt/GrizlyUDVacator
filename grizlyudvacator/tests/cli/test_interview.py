import os
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
import yaml

from grizlyudvacator.cli.io.console_io import ConsoleIO
from grizlyudvacator.cli.io.io_interface import IOInterface
from grizlyudvacator.cli.main import ask_question, load_yaml, run_interview


def test_load_yaml_valid_file():
    # Create a temporary YAML file for testing
    test_yaml = {
        "questions": [
            {"id": "test_question", "type": "boolean", "prompt": "Test question?"}
        ]
    }

    # Write to temporary file
    temp_path = "test_questions.yaml"
    with open(temp_path, "w") as f:
        yaml.dump(test_yaml, f)

    # Test loading
    loaded = load_yaml(temp_path)
    assert loaded is not None
    assert "questions" in loaded
    assert len(loaded["questions"]) == 1

    # Cleanup
    os.remove(temp_path)


def test_load_yaml_valid_file(test_io):
    """Test loading valid YAML file."""
    yaml_data = load_yaml("tests/data/test_questions.yaml", io=test_io)
    assert isinstance(yaml_data, dict)
    assert "questions" in yaml_data
    assert len(yaml_data["questions"]) > 0


def test_ask_question_boolean(test_io):
    """Test asking a boolean question."""
    q = {
        "id": "test_bool",
        "type": "boolean",
        "prompt": "Is this true?",
        "next": "next_question",
    }
    with patch("builtins.input", return_value="y"):
        answer = ask_question(q, io=test_io)
        assert answer is True


def test_ask_question_choice(test_io):
    """Test asking a choice question."""
    q = {
        "id": "test_choice",
        "type": "choice",
        "prompt": "Choose an option:",
        "options": ["Option 1", "Option 2", "Option 3"],
        "next": "next_question",
    }
    with patch("builtins.input", return_value="2"):
        answer = ask_question(q, io=test_io)
        assert answer == "Option 2"


def test_ask_question_multiple_choice(test_io):
    """Test asking a multiple choice question."""
    q = {
        "id": "test_multi",
        "type": "multiple_choice",
        "prompt": "Select options:",
        "options": ["Option A", "Option B", "Option C"],
        "next": "next_question",
    }
    with patch("builtins.input", return_value="1,3"):
        answer = ask_question(q, io=test_io)
        assert isinstance(answer, list)
        assert len(answer) == 2
        assert "Option A" in answer
        assert "Option C" in answer


def test_ask_question_date(test_io):
    """Test asking a date question."""
    q = {
        "id": "test_date",
        "type": "date",
        "prompt": "Enter a date (YYYY-MM-DD):",
        "next": "next_question",
    }
    with patch("builtins.input", return_value="2024-12-01"):
        answer = ask_question(q, io=test_io)
        assert answer == "2024-12-01"


def test_run_interview_basic_flow(test_io):
    # Create mock YAML data
    yaml_data = {
        "questions": [
            {"id": "start", "type": "boolean", "prompt": "Start?", "next": "end"},
            {"id": "end", "type": "summary", "prompt": "End"},
        ]
    }

    # Mock input
    with patch("builtins.input", side_effect=["y"]):
        # Capture print output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            answers, flags = run_interview(yaml_data, io=test_io)

            # Check output contains expected messages
            output = fake_out.getvalue()
            assert "❓ Start?" in output
            assert "📋 Interview complete" in output

            # Check results
            assert answers is not None
            assert "start" in answers
            assert answers["start"] is True
            assert flags == []


def test_run_interview_with_flags():
    # Create mock YAML with flag conditions
    yaml_data = {
        "questions": [
            {
                "id": "notice",
                "type": "boolean",
                "prompt": "Did you receive notice?",
                "next": "end",
                "flags": ["notice_received"],
            },
            {"id": "end", "type": "summary", "prompt": "End"},
        ]
    }

    # Mock input
    with patch("builtins.input", side_effect=["y"]):
        answers, flags = run_interview(yaml_data)
        assert "notice_received" in flags


def test_run_interview_with_followup():
    # Create mock YAML with follow-up logic
    yaml_data = {
        "questions": [
            {
                "id": "condition",
                "type": "boolean",
                "prompt": "Condition?",
                "next": "followup",
                "followup": {"yes": "followup"},
            },
            {"id": "followup", "type": "text", "prompt": "Follow-up", "next": "end"},
            {"id": "end", "type": "summary", "prompt": "End"},
        ]
    }

    # Mock input
    with patch("builtins.input", side_effect=["y", "followup answer"]):
        answers, flags = run_interview(yaml_data)
        assert "followup" in answers
        assert answers["followup"] == "followup answer"


def test_run_interview_with_io_interface():
    # Create mock YAML data
    yaml_data = {
        "questions": [
            {"id": "start", "type": "boolean", "prompt": "Start?", "next": "end"},
            {"id": "end", "type": "summary", "prompt": "End"},
        ]
    }

    # Create mock IO interface
    io = ConsoleIOInterface()

    # Mock input
    with patch("builtins.input", side_effect=["y"]):
        # Capture print output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            result = run_interview(yaml_data, io=io)
    assert result["answers"] == {"start": True}
    assert result["flags"] == []
    assert result["completed"] is True


def teardown_module():
    """Clean up any generated test files"""
    test_files = ["test_questions.yaml"]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
