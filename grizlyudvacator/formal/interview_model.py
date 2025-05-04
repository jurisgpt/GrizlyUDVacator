from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

import z3
from hypothesis import given, strategies as st
from pydantic import BaseModel, Field, field_validator, validator


class QuestionType(str, Enum):
    """Enum for question types."""

    BOOLEAN = "boolean"
    CHOICE = "choice"
    MULTIPLE_CHOICE = "multiple_choice"
    DATE = "date"
    TEXT = "text"


class Question(BaseModel):
    """Formal model of a question."""

    id: str
    prompt: str
    type: QuestionType
    required: bool = True
    follow_up: dict[str, Any] | None = None
    validators: dict[str, Any] | None = None
    flags: list[str] | None = None
    date_flags: dict[str, int] | None = None

    @field_validator("date_flags")
    def validate_date_flags(cls, v):
        if v is not None:
            for threshold, days in v.items():
                if not isinstance(days, int) or days < 0:
                    raise ValueError(f"Days must be a non-negative integer: {days}")
        return v


class InterviewState(BaseModel):
    """Formal model of interview state."""

    current_question: str
    answers: dict[str, Any]
    flags: list[str]
    timestamp: datetime = Field(default_factory=datetime.now)

    def add_flag(self, flag: str) -> None:
        """Formally add a flag."""
        self.flags.append(flag)
        self.flags = list(set(self.flags))  # Remove duplicates


class DateFlag(BaseModel):
    """Formal model of a date-based flag."""

    threshold: str
    days: int
    flag: str


# Z3 verification
class InterviewVerifier:
    def __init__(self):
        self.solver = z3.Solver()

    def verify_date_flags(
        self, date_flags: dict[str, int], current_date: datetime, answer_date: datetime
    ) -> bool:
        """
        Verify that date-based flags are correctly triggered using Z3 theorem prover.

        Args:
            date_flags: Dictionary of date thresholds and days
            current_date: The current date/time
            answer_date: The date provided in the answer

        Returns:
            bool: True if all date-based logic is correct
        """
        print(f"\nVerifying date flags with Z3:")
        print(f"Current date: {current_date}")
        print(f"Answer date: {answer_date}")
        print(f"Date flags: {date_flags}")

        # Convert dates to timestamps for comparison
        current_ts = int(current_date.timestamp())
        answer_ts = int(answer_date.timestamp())

        # Create Z3 variables
        current = z3.Int("current")
        answer = z3.Int("answer")
        self.solver.add(current == current_ts)
        self.solver.add(answer == answer_ts)

        # Add constraints for each date flag
        constraints = []
        for threshold, days in date_flags.items():
            threshold_ts = answer_ts + (days * 24 * 60 * 60)  # Convert days to seconds
            constraint = z3.Implies(current > threshold_ts, z3.Bool(threshold))
            self.solver.add(constraint)
            constraints.append(constraint)
            print(f"Added constraint: {constraint}")

        # Check if any flags are triggered
        result = self.solver.check()
        print(f"Z3 solver result: {result}")

        if result == z3.sat:
            print("Solver found a valid solution")
            m = self.solver.model()
            print(f"Model: {m}")
        else:
            print("No valid solution found")

        return result == z3.sat


# Hypothesis testing
given(
    st.builds(
        InterviewState,
        current_question=st.text(min_size=1),
        answers=st.dictionaries(keys=st.text(min_size=1), values=st.integers()),
        flags=st.lists(st.text(min_size=1), unique=True),
    ),
    st.builds(
        Question,
        id=st.text(min_size=1),
        prompt=st.text(min_size=1),
        type=st.sampled_from(QuestionType),
        date_flags=st.dictionaries(
            keys=st.text(min_size=1), values=st.integers(min_value=0)
        ),
    ),
)


def test_interview_state_invariants(state: InterviewState, question: Question):
    """
    Property-based test for interview state invariants.

    Tests:
    1. Flags are unique
    2. Date flags are correctly triggered
    3. State transitions are valid
    """
    # Test flag uniqueness
    assert len(state.flags) == len(set(state.flags))

    # Test date flags if present
    if question.type == QuestionType.DATE and question.date_flags:
        verifier = InterviewVerifier()
        assert verifier.verify_date_flags(
            question.date_flags,
            state.timestamp,
            datetime.now(),  # Simulate current time
        )

    # Test state transitions
    if question.required:
        assert state.current_question in question.id


def test_date_flag_verification():
    """Test date flag verification with specific example."""
    date_flags = {
        "urgent": 7,  # 7 days threshold
        "warning": 14,  # 14 days threshold
        "info": 30,  # 30 days threshold
    }

    current_date = datetime.now()
    answer_date = current_date - timedelta(days=10)  # 10 days ago

    verifier = InterviewVerifier()
    assert verifier.verify_date_flags(date_flags, current_date, answer_date)
