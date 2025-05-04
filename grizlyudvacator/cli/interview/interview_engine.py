import re
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, TypeVar, Union

from grizlyudvacator.utils.sorted_dict import sorted_dict


class QuestionType(Protocol):
    """Protocol for question types."""

    type: str
    prompt: str
    required: bool
    follow_up: dict[str, Any] | None


class NumberQuestion(QuestionType):
    """Protocol for number questions."""

    min: float | None
    max: float | None


class TextQuestion(QuestionType):
    """Protocol for text questions."""

    min_length: int | None
    max_length: int | None
    flags_from_text: dict[str, Any] | None


class DateQuestion(QuestionType):
    """Protocol for date questions."""

    date_flags: dict[str, int] | None


class ChoiceQuestion(QuestionType):
    """Protocol for choice questions."""

    options: list[str]


class MultipleChoiceQuestion(QuestionType):
    """Protocol for multiple choice questions."""

    options: list[str]
    min_choices: int | None
    max_choices: int | None


@dataclass
class Question:
    """Dataclass representing a question."""

    id: str
    type: str
    prompt: str | None = None
    required: bool = False
    follow_up: dict[str, Any] | None = None
    validators: dict[str, Any] | None = None
    flags: list[str] | None = None
    flags_from_text: dict[str, Any] | None = None
    date_flags: dict[str, int] | None = None
    options: list[str] | None = None
    min_choices: int | None = None
    max_choices: int | None = None
    min_length: int | None = None
    max_length: int | None = None
    min: float | None = None
    max: float | None = None

    def is_summary(self) -> bool:
        """Check if this is a summary question."""
        return self.type == "summary"


class Validator(Protocol):
    """Base protocol for all validators."""

    def validate(self, question: Question, answer: Any) -> None:
        """Validate the answer against the question."""
        pass


class NumberValidator:
    """Validator for number questions."""

    def validate(self, question: Question, answer: Any) -> None:
        """
        Validate number answer.

        Rule 1.2.1: Number Validation
        - Checks if answer is a number
        - Validates against min/max constraints
        """
        if not isinstance(answer, (int, float)):
            raise TypeError(f"Expected number, got {type(answer).__name__}")

        if question.min is not None and answer < question.min:
            raise ValueError(f"Value must be at least {question.min}")

        if question.max is not None and answer > question.max:
            raise ValueError(f"Value must be at most {question.max}")


class TextValidator:
    """Validator for text questions."""

    def validate(self, question: Question, answer: Any) -> None:
        """
        Validate text answer.

        Rule 1.2.2: Text Validation
        - Checks if answer is a string
        - Validates length constraints
        """
        if not isinstance(answer, str):
            raise TypeError(f"Expected string, got {type(answer).__name__}")

        if question.min_length is not None and len(answer) < question.min_length:
            raise ValueError(f"Text must be at least {question.min_length} characters")

        if question.max_length is not None and len(answer) > question.max_length:
            raise ValueError(f"Text must be at most {question.max_length} characters")


class BooleanValidator:
    """Validator for boolean questions."""

    def validate(self, question: Question, answer: Any) -> None:
        """
        Validate boolean answer.

        Rule 1.2.3: Boolean Validation
        - Checks if answer is a boolean
        """
        if not isinstance(answer, bool):
            raise TypeError(f"Expected boolean, got {type(answer).__name__}")


class DateValidator:
    """Validator for date questions."""

    def validate(self, question: Question, answer: Any) -> None:
        """
        Validate date answer.

        Rule 1.2.4: Date Validation
        - Checks if answer is a valid date string
        - Validates date range
        """
        if not isinstance(answer, str):
            raise TypeError(f"Expected string for date, got {type(answer).__name__}")

        try:
            date_obj = datetime.strptime(answer, "%Y-%m-%d").date()
            today = datetime.today().date()
            if date_obj > today:
                raise ValueError("Date cannot be in the future")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")


class ChoiceValidator:
    """Validator for choice questions."""

    def validate(self, question: Question, answer: Any) -> None:
        """
        Validate choice answer.

        Rule 1.2.5: Choice Validation
        - Checks if answer is in valid options
        """
        if not isinstance(answer, str):
            raise TypeError(f"Expected string, got {type(answer).__name__}")

        if answer not in question.options:
            raise ValueError(
                f"Invalid choice. Options are: {', '.join(question.options)}"
            )


class MultipleChoiceValidator:
    """Validator for multiple choice questions."""

    def validate(self, question: Question, answer: Any) -> None:
        """
        Validate multiple choice answer.

        Rule 1.2.6: Multiple Choice Validation
        - Checks if answer is a list of strings
        - Validates number of choices
        """
        if not isinstance(answer, list):
            raise TypeError(f"Expected list, got {type(answer).__name__}")

        invalid_choices = [
            choice for choice in answer if choice not in question.options
        ]
        if invalid_choices:
            raise ValueError(f"Invalid choices: {', '.join(invalid_choices)}")

        if question.min_choices is not None and len(answer) < question.min_choices:
            raise ValueError(f"At least {question.min_choices} choices required")

        if question.max_choices is not None and len(answer) > question.max_choices:
            raise ValueError(f"At most {question.max_choices} choices allowed")


class InterviewEngine:
    """
    Core interview logic engine that manages the flow of questions and answers.

    This class handles:
    - Question validation and type checking
    - Answer processing and storage
    - Flag management based on answers
    - Flow control between questions
    - Date and time calculations
    - Text pattern matching for flag detection

    Attributes:
        yaml_data (Dict[str, Any]): Parsed YAML data containing interview questions
        questions (Dict[str, Question]): Dictionary of questions by ID
        current_id (str): ID of the current question being processed
        answers (Dict[str, Any]): Dictionary of user answers
        flags (List[str]): List of flags triggered during interview
    """

    def __init__(self, yaml_data: dict[str, Any]) -> None:
        """
        Initialize the interview engine with YAML data.

        Args:
            yaml_data (Dict[str, Any]): The YAML data containing interview questions

        Raises:
            ValueError: If YAML data is missing required fields
            TypeError: If question types are invalid
        """
        if not yaml_data.get("questions"):
            raise ValueError("YAML data must contain questions")

        # Parse and validate questions
        questions_dict = {}
        for q in yaml_data["questions"]:
            try:
                # For summary questions, we don't require all fields
                if q["type"] == "summary":
                    question = Question(id=q["id"], type=q["type"], required=False)
                else:
                    question = Question(
                        id=q["id"],
                        prompt=q["prompt"],
                        type=q["type"],
                        required=q.get("required", False),
                        follow_up=q.get("follow_up"),
                        validators=q.get("validators"),
                        flags=q.get("flags", []),
                        flags_from_text=q.get("flags_from_text"),
                        date_flags=q.get("date_flags"),
                        options=q.get("options", []),
                        min_choices=q.get("min_choices"),
                        max_choices=q.get("max_choices"),
                        min_length=q.get("min_length"),
                        max_length=q.get("max_length"),
                        min=q.get("min"),
                        max=q.get("max"),
                    )
                questions_dict[q["id"]] = question
            except KeyError as e:
                raise ValueError(
                    f"Missing required field in question {q.get('id')}: {e}"
                )
            except TypeError as e:
                raise ValueError(f"Invalid type in question {q.get('id')}: {e}")

        self.yaml_data = yaml_data
        self.questions = questions_dict
        self.current_id = yaml_data.get("start_id", yaml_data["questions"][0]["id"])
        self.answers: dict[str, Any] = {}
        self.flags: list[str] = []
        self.flag_priorities: dict[str, int] = {}  # Store flag priorities
        self.sorted_flags: OrderedDict[str, int] = OrderedDict()  # Store sorted flags

        # Validate that all referenced questions exist
        self._validate_question_references()

        # Validate flow control
        self._validate_flow_control()

    def _validate_question_references(self) -> None:
        """Validate that all referenced questions exist."""
        for question in self.questions.values():
            if question.follow_up:
                if isinstance(question.follow_up, dict):
                    # Check next question references
                    if "next" in question.follow_up:
                        next_id = question.follow_up["next"]
                        if next_id not in self.questions:
                            raise ValueError(
                                f"Question {question.id} references non-existent question {next_id}"
                            )
                    # Check flag references
                    if "flags" in question.follow_up:
                        for flag in question.follow_up["flags"]:
                            # We don't validate flag names here as they might be dynamically generated
                            pass
                elif isinstance(question.follow_up, str):
                    if question.follow_up not in self.questions:
                        raise ValueError(
                            f"Question {question.id} references non-existent question {question.follow_up}"
                        )
                else:
                    raise ValueError(
                        f"Invalid follow_up format in question {question.id}"
                    )

    def _validate_flow_control(self) -> None:
        """Validate the flow control logic."""
        # Check if start_id exists if specified
        if "start_id" in self.yaml_data:
            start_id = self.yaml_data["start_id"]
            if start_id not in self.questions:
                raise ValueError(f"Start question {start_id} does not exist")

        # Check if there are any circular references
        visited = set()
        current = self.current_id

        while current:
            if current in visited:
                raise ValueError(f"Circular reference detected in question flow")
            visited.add(current)

            question = self.questions[current]
            if question.follow_up:
                if isinstance(question.follow_up, dict):
                    current = question.follow_up.get("next")
                else:
                    current = question.follow_up
            else:
                current = None

    def add_flag(self, flag: str, priority: int = 5) -> None:
        """
        Add a flag with optional priority.

        Args:
            flag (str): The flag to add
            priority (int): Priority level (default 5)
        """
        self.flags.append(flag)
        self.flag_priorities[flag] = priority
        # Sort flags by priority whenever a new one is added
        self.sorted_flags = sorted_dict(self.flag_priorities)

    def process_answer(self, question_id: str, answer: Any) -> str | None:
        """
        Process a question and its answer, returning the next question ID.

        Rule 1.0: Core Answer Processing
        - Validates question existence
        - Handles required fields
        - Validates answer types
        - Processes answer storage
        - Manages flag collection
        - Handles follow-up logic

        Args:
            question_id (str): ID of the current question
            answer (Any): User's answer to the question

        Returns:
            Optional[str]: ID of the next question, or None if interview is complete

        Raises:
            KeyError: If question ID is not found
            TypeError: If answer type doesn't match expected type
            ValueError: If answer fails validation
        """
        try:
            question = self.questions[question_id]
        except KeyError:
            raise KeyError(f"Question ID not found: {question_id}")

        # Rule 1.1: Required Field Validation
        if question.required and not answer:
            return question_id  # Return same question ID to retry

        # Rule 1.2: Type Validation and Processing
        validator = self._get_validator(question.type)
        if validator:
            validator.validate(question, answer)

        # Rule 1.3: Answer Storage
        self.answers[question_id] = answer

        # Rule 2.0: Flag Management
        self._process_flags(question, answer)

        # Rule 3.0: Flow Control
        return self._get_next_question_id(question, answer)

    def _get_validator(self, question_type: str) -> Optional["Validator"]:
        """Get appropriate validator for question type."""
        validators = {
            "number": NumberValidator(),
            "text": TextValidator(),
            "boolean": BooleanValidator(),
            "date": DateValidator(),
            "choice": ChoiceValidator(),
            "multiple_choice": MultipleChoiceValidator(),
        }
        return validators.get(question_type)

    def _process_flags(self, question: Question, answer: Any) -> None:
        """Process all types of flags for a question."""
        # Rule 2.1: Static Flags
        if question.flags:
            self.flags.extend(question.flags)

        # Rule 2.2: Text Pattern Flags
        if (
            question.type == "text"
            and question.flags_from_text
            and isinstance(answer, str)
        ):
            self._process_text_flags(question, answer)

        # Rule 2.3: Date-Based Flags
        if question.type == "date" and question.date_flags and answer:
            self._process_date_flags(question, answer)

        # Rule 2.4: Choice-Based Flags
        if question.type in ["choice", "multiple_choice"] and question.follow_up:
            self._process_choice_flags(question, answer)

        # Validate answer type
        if q.get("type") == "number":
            if not isinstance(answer, (int, float)):
                raise TypeError(f"Expected number, got {type(answer).__name__}")
            if q.get("min") is not None and answer < q["min"]:
                return question_id  # Return same question ID to retry
            if q.get("max") is not None and answer > q["max"]:
                return question_id  # Return same question ID to retry

        elif q.get("type") == "boolean":
            if not isinstance(answer, bool):
                raise TypeError(f"Expected boolean, got {type(answer).__name__}")

        elif q.get("type") == "text":
            if not isinstance(answer, str):
                raise TypeError(f"Expected string, got {type(answer).__name__}")

        elif q.get("type") == "date":
            if not isinstance(answer, str):
                raise TypeError(
                    f"Expected string for date, got {type(answer).__name__}"
                )
            try:
                date_obj = datetime.datetime.strptime(answer, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")

        # Store answer
        self.answers[question_id] = answer

        # Capture static flags
        if "flags" in q:
            if not isinstance(q["flags"], list):
                raise TypeError("Flags must be a list")
            self.flags.extend(q["flags"])

        # Keyword-based flag detection using regex
        if q["type"] == "text" and "flags_from_text" in q and isinstance(answer, str):
            keywords = q["flags_from_text"].get("keywords", [])
            if not isinstance(keywords, list):
                raise TypeError("Keywords must be a list")

            keywords_dict = {}
            for item in keywords:
                if not isinstance(item, dict) or len(item) != 1:
                    raise ValueError("Invalid keyword format")

                key = next(iter(item))
                value = item[key]
                keywords_dict[key] = value

            for label, pattern in keywords_dict.items():
                if re.search(rf"\b{pattern}\b", answer, re.IGNORECASE):
                    self.flags.append(label)

        # Calculate time-based flags if dates are involved
        if q["type"] == "date" and "date_flags" in q and answer:
            try:
                date_obj = datetime.datetime.strptime(answer, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")

            today = datetime.date.today()
            days_diff = (today - date_obj).days

            for flag, threshold in q["date_flags"].items():
                if not isinstance(threshold, int):
                    raise TypeError("Date flag thresholds must be integers")
                if days_diff >= threshold:
                    self.flags.append(flag)

        # Determine next step
        if "follow_up" in q:
            if not isinstance(q["follow_up"], dict):
                raise TypeError("Follow-up must be a dictionary")

            if isinstance(answer, bool):
                branch = "if_true" if answer else "if_false"
                next_info = q["follow_up"].get(branch, {})
                if not isinstance(next_info, dict):
                    raise TypeError("Next info must be a dictionary")

                self.flags.extend(next_info.get("flags", []))
                return next_info.get("next")

            elif isinstance(answer, str) and "options" in q["follow_up"]:
                if not isinstance(q["follow_up"]["options"], dict):
                    raise TypeError("Options must be a dictionary")

                next_info = q["follow_up"]["options"].get(answer, {})
                if not isinstance(next_info, dict):
                    raise TypeError("Next info must be a dictionary")

                self.flags.extend(next_info.get("flags", []))
                return next_info.get("next", q.get("next"))

            else:
                return q.get("next")

        return q.get("next")

    def get_question(self, question_id: str) -> dict[str, Any]:
        """
        Retrieve a question by its ID.

        Rule 4.0: Question Retrieval
        - Validates question existence
        - Returns question dictionary
        - Raises error if not found

        Args:
            question_id (str): ID of the question to retrieve

        Returns:
            Dict[str, Any]: The question dictionary containing:
                - id: Question identifier
                - prompt: Question text
                - type: Question type (text, number, boolean, etc.)
                - required: Whether answer is required
                - follow_up: Next question logic
                - validators: Validation rules
                - flags: Static flags to set
                - flags_from_text: Text pattern flags
                - date_flags: Time-based flags

        Raises:
            KeyError: If question ID is not found
        """
        # ... (rest of the method remains the same)

    def _process_date_flags(self, question: Question, answer: str) -> None:
        """
        Rule 2.3: Process date-based flags based on time calculations.

        This method handles:
        1. Text-based flag processing using keywords
        2. Date-based flag processing using time thresholds
        3. Flow control based on follow-up logic
        """
        # Process text-based flags
        if question.flags_from_text:
            keywords = question.flags_from_text.get("keywords", [])
            if isinstance(keywords, list):
                keywords_dict = {}
                for item in keywords:
                    if isinstance(item, dict) and len(item) == 1:
                        key = next(iter(item))
                        value = item[key]
                        keywords_dict[key] = value
                keywords = keywords_dict

            for label, pattern in keywords.items():
                if re.search(rf"\b{pattern}\b", answer, re.IGNORECASE):
                    self.flags.append(label)

        # Calculate time-based flags if dates are involved
        if question.type == "date" and question.date_flags and answer:
            try:
                date_obj = datetime.strptime(answer, "%Y-%m-%d").date()
                today = datetime.now().date()
                days_diff = (today - date_obj).days

                for flag, threshold in question.date_flags.items():
                    if days_diff >= threshold:
                        self.flags.append(flag)
            except ValueError:
                pass

        # Determine next step
        if question.follow_up:
            if isinstance(answer, bool):
                branch = "if_true" if answer else "if_false"
                next_info = question.follow_up.get(branch, {})
                self.flags.extend(next_info.get("flags", []))
                return next_info.get("next")
            elif isinstance(answer, str) and "options" in question.follow_up:
                next_info = question.follow_up["options"].get(answer, {})
                self.flags.extend(next_info.get("flags", []))
                return next_info.get("next", question.get("next"))
            else:
                return question.get("next")
        return None

    def get_answers(self) -> dict[str, Any]:
        """Get the collected answers."""
        return self.answers

    def get_sorted_flags(self) -> OrderedDict[str, int]:
        """
        Get flags sorted by priority.

        Returns:
            OrderedDict: Flags sorted by priority (highest priority first)
        """
        return self.sorted_flags

    def get_flags(self) -> list[str]:
        """Get the triggered flags."""
        return list(set(self.flags))  # Remove duplicates

    def is_complete(self) -> bool:
        """Check if the interview is complete."""
        return self.current_id is None

    def get_current_question(self) -> dict[str, Any]:
        """Get the current question."""
        return self.questions[self.current_id] if self.current_id else None
