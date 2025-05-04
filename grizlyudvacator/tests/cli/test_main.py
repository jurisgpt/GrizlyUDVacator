from unittest.mock import MagicMock, patch

import pytest

from grizlyudvacator.cli.main import ask_question


def test_ask_boolean_yes():
    with patch("builtins.input", return_value="y"):
        result = ask_question({"type": "boolean", "prompt": "Test question"})
        assert result is True


def test_ask_boolean_no():
    with patch("builtins.input", return_value="n"):
        result = ask_question({"type": "boolean", "prompt": "Test question"})
        assert result is False


def test_ask_text():
    test_input = "test answer"
    with patch("builtins.input", return_value=test_input):
        result = ask_question({"type": "text", "prompt": "Test question"})
        assert result == test_input


def test_ask_date_valid():
    test_date = "2025-05-03"
    with patch("builtins.input", return_value=test_date):
        result = ask_question({"type": "date", "prompt": "Test date"})
        assert result == test_date


def test_ask_choice():
    test_options = ["option1", "option2"]
    with patch("builtins.input", return_value="1"):
        result = ask_question(
            {"type": "choice", "prompt": "Test question", "options": test_options}
        )
        assert result == test_options[0]
