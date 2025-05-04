from datetime import datetime
from io import StringIO

import pytest
import yaml
from hypothesis import example, given, strategies as st
from hypothesis.strategies import (
    booleans,
    dates,
    dictionaries,
    fixed_dictionaries,
    lists,
    sampled_from,
    text,
)

from grizlyudvacator.backend.interview.interview_engine import InterviewEngine
from grizlyudvacator.cli.io.console_io import ConsoleIO
from grizlyudvacator.cli.io.io_interface import IOInterface
from grizlyudvacator.utils.date_utils import is_future_date, parse_date


@pytest.fixture
def test_io():
    class TestIO(IOInterface):
        def __init__(self):
            self.responses = {}
            self.questions_asked = []
            self.files_written = []
            self.files = {}

        def ask_question(self, question):
            self.questions_asked.append(question)
            return self.responses.get(question["id"], None)

        def write_output(self, text):
            pass

        def reset(self):
            self.responses = {}
            self.questions_asked = []
            self.files_written = []
            self.files = {}

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


def generate_question_strategy():
    """Generate valid question strategies."""
    return st.fixed_dictionaries(
        {
            "id": st.text(
                alphabet=st.characters(blacklist_categories=("Cc", "Cs")), min_size=1
            ),
            "type": st.sampled_from(
                ["boolean", "text", "date", "choice", "multiple_choice"]
            ),
            "prompt": st.text(),
            "next": st.one_of(st.none(), st.text()),
            "flags": st.lists(st.text()),
            "follow_up": st.fixed_dictionaries(
                {
                    "if_true": st.fixed_dictionaries(
                        {
                            "next": st.one_of(st.none(), st.text()),
                            "flags": st.lists(st.text()),
                        }
                    ),
                    "if_false": st.fixed_dictionaries(
                        {
                            "next": st.one_of(st.none(), st.text()),
                            "flags": st.lists(st.text()),
                        }
                    ),
                }
            ),
        }
    )


def generate_answer_strategy(question_type: str):
    """Generate valid answers for question types."""
    if question_type == "boolean":
        return st.booleans()
    elif question_type == "text":
        return st.text()
    elif question_type == "date":
        return dates(min_value=datetime(1900, 1, 1), max_value=datetime.now()).map(
            lambda d: d.strftime("%Y-%m-%d")
        )
    elif question_type == "choice":
        return sampled_from(["option1", "option2", "option3"])
    elif question_type == "multiple_choice":
        return st.lists(text(min_size=1), min_size=1, max_size=3)
    return None


def generate_yaml_strategy():
    """Generate valid YAML structures."""
    return lists(generate_question_strategy(), min_size=1, max_size=10).map(
        lambda questions: {"questions": questions}
    )


def generate_test_data():
    """Generate test data with known values."""
    return (
        {
            "questions": [
                {
                    "id": "q1",
                    "type": "boolean",
                    "prompt": "Test question",
                    "next": "q2",
                    "flags": ["test_flag"],
                },
                {
                    "id": "q2",
                    "type": "text",
                    "prompt": "Another question",
                    "next": None,
                },
            ]
        },
        "q1",
        True,
    )


@given(yaml_data=generate_yaml_strategy())
def test_engine_initialization(yaml_data):
    """Test that engine initializes with valid YAML."""
    if not yaml_data["questions"]:  # Skip if no questions
        return

    engine = InterviewEngine(yaml_data)
    first_question = yaml_data["questions"][0]

    # Verify initial state
    assert engine.current_id == first_question["id"]
    assert len(engine.questions) == len(yaml_data["questions"])
    assert engine.answers == {}  # No answers initially
    assert engine.flags == []  # No flags initially

    # Verify question lookup
    for q in yaml_data["questions"]:
        try:
            retrieved_q = engine.get_question(q["id"])
            assert retrieved_q == q
        except KeyError:
            pytest.fail(f"Question {q['id']} not found in engine")


@example(*generate_test_data())
@given(
    yaml_data=generate_yaml_strategy(),
    question_id=st.text(),
    answer=generate_answer_strategy(
        st.sampled_from(["boolean", "text", "date", "choice", "multiple_choice"])
    ),
)
def test_engine_process_question(yaml_data, question_id, answer):
    """Test question processing."""
    if not yaml_data["questions"]:  # Skip if no questions
        return

    engine = InterviewEngine(yaml_data)

    try:
        # Try to process a question
        next_id = engine.process_question(question_id, answer)

        # Verify state after processing
        assert question_id in engine.answers
        assert engine.answers[question_id] == answer

        # Verify next question ID
        if next_id:
            assert (
                next_id in engine.questions
            ), f"Next ID {next_id} not found in questions"
        else:
            assert engine.is_complete()

        # Verify flags are added
        results = engine.get_results()
        assert isinstance(results["flags"], list)
        assert all(isinstance(f, str) for f in results["flags"])

    except KeyError:
        # Question ID not found - valid failure case
        assert question_id not in engine.questions
        assert question_id not in engine.answers


@example(*generate_test_data())
@given(yaml_data=generate_yaml_strategy())
def test_engine_question_flow(yaml_data):
    """Test complete question flow."""
    if not yaml_data["questions"]:  # Skip if no questions
        return

    engine = InterviewEngine(yaml_data)
    current_id = engine.current_id

    # Track visited questions and their answers
    visited = set()
    answers = {}

    while current_id:
        q = engine.get_question(current_id)

        # Generate appropriate answer based on question type
        answer = generate_answer_strategy(q["type"]).example()

        # Process question
        next_id = engine.process_question(current_id, answer)

        # Track visit and answer
        visited.add(current_id)
        answers[current_id] = answer

        # Verify state
        assert current_id in engine.answers
        assert engine.answers[current_id] == answer

        # Move to next question
        current_id = next_id

    assert engine.is_complete()
    results = engine.get_results()

    # Verify results
    assert isinstance(results["answers"], dict)
    assert isinstance(results["flags"], list)
    assert len(results["answers"]) == len(visited)
    assert all(isinstance(f, str) for f in results["flags"])

    # Verify all answers were processed
    for q_id, ans in answers.items():
        assert q_id in results["answers"]
        assert results["answers"][q_id] == ans


@example(*generate_test_data())
@given(
    yaml_data=generate_yaml_strategy(),
    question_id=st.text(),
    answer=generate_answer_strategy(
        st.sampled_from(["boolean", "text", "date", "choice", "multiple_choice"])
    ),
)
def test_engine_flag_detection(yaml_data, question_id, answer):
    """Test flag detection logic."""
    if not yaml_data["questions"]:  # Skip if no questions
        return

    # Add flag detection to a random question
    question = yaml_data["questions"][0]

    # Add different types of flags
    flags = ["test_flag"]
    if isinstance(answer, str):
        flags.append("text_flag")
    if isinstance(answer, bool):
        flags.append("boolean_flag")

    question["flags"] = flags

    engine = InterviewEngine(yaml_data)

    try:
        # Process question
        engine.process_question(question_id, answer)
        results = engine.get_results()

        # Verify flags
        assert isinstance(results["flags"], list)
        assert all(isinstance(f, str) for f in results["flags"])

        # Verify flag presence
        if question_id == question["id"]:
            # All flags should be present
            for flag in flags:
                assert flag in results["flags"], f"Flag {flag} not found in results"

            # Verify no duplicate flags
            assert len(results["flags"]) == len(set(results["flags"]))

            # Verify flag order
            flag_order = [f for f in flags if f in results["flags"]]
            assert flag_order == sorted(flag_order)

        else:
            assert question_id not in engine.questions
            assert question_id not in engine.answers

    except KeyError:
        # Question ID not found - valid failure case
        assert question_id not in engine.questions
        assert question_id not in engine.answers
    except Exception as e:
        # Log unexpected errors
        print(f"Unexpected error: {str(e)}")
        raise


@example(
    {
        "questions": [
            {
                "id": "q1",
                "type": "date",
                "prompt": "Date question",
                "date_flags": {"old_date": 365, "recent_date": 30, "future_date": -30},
            }
        ]
    },
    "q1",
    "2025-01-01",
)
@example(
    {
        "questions": [
            {
                "id": "q1",
                "type": "date",
                "prompt": "Date question",
                "date_flags": {"past_year": 365, "this_year": 0, "next_year": -365},
            }
        ]
    },
    "q1",
    "2024-01-01",
)
@given(yaml_data=generate_yaml_strategy())
def test_engine_date_flags(yaml_data):
    """Test date-based flag detection."""
    if not yaml_data["questions"]:  # Skip if no questions
        return

    # Add date flags to a random question
    question = yaml_data["questions"][0]
    question["type"] = "date"

    # Add various date flags
    question["date_flags"] = {
        "old_date": 365,  # More than 1 year old
        "recent_date": 30,  # Less than 30 days old
        "future_date": -30,  # More than 30 days in future
        "past_year": 365,  # More than 1 year old
        "this_year": 0,  # This year
        "next_year": -365,  # Next year
    }

    engine = InterviewEngine(yaml_data)

    # Test various date scenarios
    test_dates = {
        "old": (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d"),
        "recent": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
        "future": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
        "past_year": (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d"),
        "this_year": datetime.now().strftime("%Y-%m-%d"),
        "next_year": (datetime.now() + timedelta(days=400)).strftime("%Y-%m-%d"),
    }

    for name, date in test_dates.items():
        date_str = date.strftime("%Y-%m-%d")
        engine.process_question(question["id"], date_str)
        results = engine.get_results()

        # Verify date format
        assert isinstance(results["answers"][question["id"]], str)
        assert len(results["answers"][question["id"]]) == 10

        # Verify appropriate flags
        if name == "old":
            assert "old_date" in results["flags"]
            assert "past_year" in results["flags"]
        elif name == "recent":
            assert "recent_date" in results["flags"]
        elif name == "future":
            assert "future_date" in results["flags"]
        elif name == "this_year":
            assert "this_year" in results["flags"]
        elif name == "next_year":
            assert "next_year" in results["flags"]

        # Verify no duplicate flags
        assert len(results["flags"]) == len(set(results["flags"]))

        # Verify flag order (alphabetical)
        flag_order = sorted(results["flags"])
        assert flag_order == results["flags"]


@given(
    yaml_data=generate_yaml_strategy(),
    question_id=st.text(),
    answer=st.one_of(
        st.booleans(),
        st.text(),
        st.dates(),
        st.sampled_from(["option1", "option2", "option3"]),
        st.lists(st.sampled_from(["option1", "option2", "option3"]), min_size=1),
    ),
)
def test_engine_process_question(yaml_data, question_id, answer):
    """Test question processing."""
    if not yaml_data["questions"]:  # Skip if no questions
        return

    engine = InterviewEngine(yaml_data)

    try:
        # Try to process a question
        next_id = engine.process_question(question_id, answer)

        # Verify state after processing
        assert question_id in engine.answers
        assert engine.answers[question_id] == answer

        # Verify next question ID
        if next_id:
            assert (
                next_id in engine.questions
            ), f"Next ID {next_id} not found in questions"
        else:
            assert engine.is_complete()

        # Verify flags are added
        results = engine.get_results()
        assert isinstance(results["flags"], list)
        assert all(isinstance(f, str) for f in results["flags"])

    except KeyError:
        # Question ID not found - valid failure case
        assert question_id not in engine.questions
        assert question_id not in engine.answers


@example(
    {
        "questions": [
            {"id": "q1", "type": "boolean", "prompt": "Test question", "next": "q2"},
            {"id": "q2", "type": "text", "prompt": "Another question", "next": None},
        ]
    }
)
@example(
    {
        "questions": [
            {
                "id": "q1",
                "type": "choice",
                "prompt": "Choose one",
                "options": ["option1", "option2"],
                "next": "q2",
            },
            {
                "id": "q2",
                "type": "multiple_choice",
                "prompt": "Choose many",
                "options": ["option1", "option2", "option3"],
                "next": None,
            },
        ]
    }
)
@example(
    {
        "questions": [
            {
                "id": "q1",
                "type": "date",
                "prompt": "Date question",
                "date_flags": {"old_date": 365, "recent_date": 30},
                "next": None,
            }
        ]
    }
)
@given(yaml_data=generate_yaml_strategy())
def test_engine_question_flow(yaml_data):
    """Test complete question flow."""
    if not yaml_data["questions"]:  # Skip if no questions
        return

    engine = InterviewEngine(yaml_data)
    current_id = engine.current_id

    # Track visited questions and their answers
    visited = set()
    answers = {}

    while current_id:
        q = engine.get_question(current_id)

        # Generate appropriate answer based on question type
        if q["type"] == "boolean":
            answer = True  # Simple boolean
        elif q["type"] == "text":
            answer = "test answer"
        elif q["type"] == "choice":
            answer = q["options"][0]  # First option
        elif q["type"] == "multiple_choice":
            answer = [q["options"][0]]  # First option
        elif q["type"] == "date":
            answer = "2025-01-01"
        else:
            answer = "default answer"

        # Process question
        next_id = engine.process_question(current_id, answer)

        # Track visit and answer
        visited.add(current_id)
        answers[current_id] = answer

        # Verify state
        assert current_id in engine.answers
        assert engine.answers[current_id] == answer

        # Move to next question
        current_id = next_id

    assert engine.is_complete()
    results = engine.get_results()

    # Verify results
    assert isinstance(results["answers"], dict)
    assert isinstance(results["flags"], list)
    assert len(results["answers"]) == len(visited)
    assert all(isinstance(f, str) for f in results["flags"])

    # Verify all answers were processed
    for q_id, ans in answers.items():
        assert q_id in results["answers"]
        assert results["answers"][q_id] == ans


@example(
    {
        "questions": [
            {
                "id": "q1",
                "type": "boolean",
                "prompt": "Test question",
                "flags": ["test_flag"],
            }
        ]
    },
    "q1",
    True,
)
@example(
    {
        "questions": [
            {
                "id": "q1",
                "type": "text",
                "prompt": "Test question",
                "flags_from_text": {"keywords": {"emergency": "emergency_flag"}},
            }
        ]
    },
    "q1",
    "emergency situation",
)
@example(
    {
        "questions": [
            {
                "id": "q1",
                "type": "choice",
                "prompt": "Test question",
                "options": ["option1", "option2"],
                "flags": ["choice_flag"],
            }
        ]
    },
    "q1",
    "option1",
)
@given(
    yaml_data=generate_yaml_strategy(),
    question_id=st.text(),
    answer=st.one_of(
        st.booleans(),
        st.text(),
        st.dates(),
        st.sampled_from(["option1", "option2", "option3"]),
        st.lists(st.sampled_from(["option1", "option2", "option3"]), min_size=1),
    ),
)
def test_engine_flag_detection(yaml_data, question_id, answer):
    """Test flag detection logic."""
    if not yaml_data["questions"]:  # Skip if no questions
        return

    # Add flag detection to a random question
    question = yaml_data["questions"][0]

    # Add different types of flags
    flags = ["test_flag"]
    if isinstance(answer, str):
        flags.append("text_flag")
    if isinstance(answer, bool):
        flags.append("boolean_flag")

    question["flags"] = flags

    engine = InterviewEngine(yaml_data)

    try:
        # Process question
        engine.process_question(question_id, answer)
        results = engine.get_results()

        # Verify flags
        assert isinstance(results["flags"], list)
        assert all(isinstance(f, str) for f in results["flags"])

        # Verify flag presence
        if question_id == question["id"]:
            # All flags should be present
            for flag in flags:
                assert flag in results["flags"], f"Flag {flag} not found in results"

            # Verify no duplicate flags
            assert len(results["flags"]) == len(set(results["flags"]))

            # Verify flag order
            flag_order = [f for f in flags if f in results["flags"]]
            assert flag_order == sorted(flag_order)

        else:
            assert question_id not in engine.questions
            assert question_id not in engine.answers

    except KeyError:
        # Question ID not found - valid failure case
        assert question_id not in engine.questions
        assert question_id not in engine.answers
    except Exception as e:
        # Log unexpected errors
        print(f"Unexpected error: {str(e)}")
        raise


@example(
    {
        "questions": [
            {
                "id": "q1",
                "type": "date",
                "prompt": "Date question",
                "date_flags": {"old_date": 365, "recent_date": 30, "future_date": -30},
            }
        ]
    },
    "q1",
    "2025-01-01",
)
@example(
    {
        "questions": [
            {
                "id": "q1",
                "type": "date",
                "prompt": "Date question",
                "date_flags": {"past_year": 365, "this_year": 0, "next_year": -365},
            }
        ]
    },
    "q1",
    "2024-01-01",
)
@given(yaml_data=generate_yaml_strategy())
def test_engine_date_flags(yaml_data):
    """Test date-based flag detection."""
    if not yaml_data["questions"]:  # Skip if no questions
        return

    # Add date flags to a random question
    question = yaml_data["questions"][0]
    question["type"] = "date"

    # Add various date flags
    question["date_flags"] = {
        "old_date": 365,  # More than 1 year old
        "recent_date": 30,  # Less than 30 days old
        "future_date": -30,  # More than 30 days in future
        "past_year": 365,  # More than 1 year old
        "this_year": 0,  # This year
        "next_year": -365,  # Next year
    }

    engine = InterviewEngine(yaml_data)

    # Test various date scenarios
    test_dates = {
        "old": (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d"),
        "recent": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
        "future": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
        "past_year": (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d"),
        "this_year": datetime.now().strftime("%Y-%m-%d"),
        "next_year": (datetime.now() + timedelta(days=400)).strftime("%Y-%m-%d"),
    }

    for name, date in test_dates.items():
        date_str = date.strftime("%Y-%m-%d")
        engine.process_question(question["id"], date_str)
        results = engine.get_results()

        # Verify date format
        assert isinstance(results["answers"][question["id"]], str)
        assert len(results["answers"][question["id"]]) == 10

        # Verify appropriate flags
        if name == "old":
            assert "old_date" in results["flags"]
            assert "past_year" in results["flags"]
        elif name == "recent":
            assert "recent_date" in results["flags"]
        elif name == "future":
            assert "future_date" in results["flags"]
        elif name == "this_year":
            assert "this_year" in results["flags"]
        elif name == "next_year":
            assert "next_year" in results["flags"]

        # Verify no duplicate flags
        assert len(results["flags"]) == len(set(results["flags"]))

        # Verify flag order (alphabetical)
        flag_order = sorted(results["flags"])
        assert flag_order == results["flags"]
