from datetime import datetime, timedelta

import pytest
from hypothesis import given, strategies as st
from pydantic import ValidationError
from pytest import raises

from grizlyudvacator.formal.interview_model import (
    InterviewState,
    InterviewVerifier,
    Question,
    QuestionType,
)


def test_question_validation():
    """Test question validation."""
    # Valid question
    valid_question = Question(
        id="test_question",
        prompt="Test prompt",
        type=QuestionType.DATE,
        date_flags={"urgent": 7},
    )
    assert valid_question.id == "test_question"

    # Invalid date flags (negative days)
    with pytest.raises(ValidationError):
        Question(
            id="invalid_question",
            prompt="Test prompt",
            type=QuestionType.DATE,
            date_flags={"urgent": -1},  # Negative days should fail
        )


def test_date_flag_verification():
    """Test date flag verification."""
    verifier = InterviewVerifier()

    # Test case where flags should trigger
    date_flags = {
        "urgent": 7,  # 7 days threshold
        "warning": 14,  # 14 days threshold
        "info": 30,  # 30 days threshold
    }

    current_date = datetime.now()
    answer_date = current_date - timedelta(days=10)  # 10 days ago

    # Should trigger urgent and warning flags
    assert verifier.verify_date_flags(date_flags, current_date, answer_date)

    # Test case where no flags should trigger
    answer_date = current_date - timedelta(days=1)  # Only 1 day ago
    assert not verifier.verify_date_flags(date_flags, current_date, answer_date)


def test_interview_state():
    """Test interview state management."""
    state = InterviewState(
        current_question="start", answers={"start": True}, flags=["started"]
    )

    # Test adding a new flag
    state.add_flag("new_flag")
    assert "new_flag" in state.flags

    # Test duplicate flag handling
    state.add_flag("new_flag")
    assert state.flags.count("new_flag") == 1  # Should only be one instance
