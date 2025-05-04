from argparse import Namespace
from unittest.mock import patch

import pytest

from grizlyudvacator.cli.main import load_yaml, run_interview


@patch("builtins.input", side_effect=["n"])
def test_simple_yaml(mock_input, capsys):
    """Test running interview with simple YAML file."""
    # Load YAML and run interview
    yaml_data = load_yaml("tests/data/interview_demo.yaml")
    answers, flags = run_interview(yaml_data)

    # Capture and verify output
    captured = capsys.readouterr()
    output = captured.out

    assert "❓ Did you respond to the court papers?" in output
    assert "Enter [y/n]:" in output
    assert "📊 INTERVIEW SUMMARY" in output
    assert "  - intro: False" in output


def test_complex_yaml(capsys):
    """Test running interview with complex YAML file."""
    user_inputs = [
        "John Doe",  # name
        "25",  # age
        "y",  # has_children
        "2",  # children_count
    ]

    with patch("builtins.input", side_effect=user_inputs):
        yaml_data = load_yaml("tests/data/interview_complex.yaml")
        answers, flags = run_interview(yaml_data)

    captured = capsys.readouterr()
    output = captured.out

    # Verify all questions were asked
    assert "❓ What is your full name?" in output
    assert "Enter [y/n]:" in output
    assert "📊 INTERVIEW SUMMARY" in output
    assert "🧾 Collected Answers:" in output
    # Verify summary output
    assert "  - name: John Doe" in output
    assert "  - age: 25" in output
    assert "  - has_children: Yes" in output
    assert "  - children_count: 2" in output


def test_validation_failure(capsys):
    """Test validation failure handling."""
    user_inputs = [
        "John Doe",  # name
        "15",  # age (should fail validation)
        "y",  # retry age
        "25",  # valid age
        "y",  # has_children
        "0",  # children_count (should fail validation)
        "y",  # retry children_count
        "2",  # valid children_count
    ]

    with patch("builtins.input", side_effect=user_inputs):
        yaml_data = load_yaml("tests/data/interview_complex.yaml")
        answers, flags = run_interview(yaml_data)

    captured = capsys.readouterr()
    output = captured.out

    # Verify validation error messages
    import re

    assert re.search(r"⚠️\ufe0f? Value must be at least 18", output)
    assert re.search(r"⚠️\ufe0f? Value must be at most 120", output)
    assert re.search(r"⚠️\ufe0f? Value must be at least 1", output)
    assert re.search(r"⚠️\ufe0f? Value must be at most 10", output)

    # Verify final successful answers
    assert "  - age: 25" in output
    assert "  - children_count: 2" in output


def test_required_field(capsys):
    """Test handling of required fields."""
    user_inputs = [
        "",  # empty name (should fail)
        "y",  # retry name
        "John Doe",  # valid name
        "25",  # age
        "y",  # has_children
        "2",  # children_count
    ]

    with patch("builtins.input", side_effect=user_inputs):
        yaml_data = load_yaml("tests/data/interview_complex.yaml")
        answers, flags = run_interview(yaml_data)

    captured = capsys.readouterr()
    output = captured.out

    # Verify required field validation
    assert "⚠️ This field is required." in output

    # Verify final successful answers
    assert "  - name: John Doe" in output
