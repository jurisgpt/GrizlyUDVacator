from datetime import datetime, timedelta
from typing import Any, Dict, Optional


class InterviewEngine:
    """Core interview logic engine."""

    def __init__(self, yaml_data: dict[str, Any]):
        """Initialize with YAML data."""
        self.yaml_data = yaml_data
        self.questions = self._load_questions()
        self.answers = {}
        self.current_id = self._get_start_id()
        self.flags = []

    def _load_questions(self) -> dict[str, Any]:
        """Load questions from YAML data."""
        return {q["id"]: q for q in self.yaml_data.get("questions", [])}

    def _get_start_id(self) -> str | None:
        """Get the starting question ID."""
        return next(iter(self.questions), None)

    def process_question(self, question_id: str, answer: Any) -> str | None:
        """Process a question and its answer."""
        if question_id not in self.questions:
            return None

        question = self.questions[question_id]
        self.answers[question_id] = answer

        # Handle flags
        if "flags" in question:
            self.flags.extend(question["flags"])

        # Handle date flags
        if question.get("type") == "date":
            self._process_date_flags(question_id, answer)

        # Get next question
        next_id = question.get("next")
        if next_id and next_id in self.questions:
            return next_id

        # Check for follow-up questions
        if "follow_up" in question:
            if answer is True and "if_true" in question["follow_up"]:
                return question["follow_up"]["if_true"].get("next")
            elif answer is False and "if_false" in question["follow_up"]:
                return question["follow_up"]["if_false"].get("next")

        return None

    def _process_date_flags(self, question_id: str, answer: str):
        """Process date-based flags."""
        try:
            date = datetime.strptime(answer, "%Y-%m-%d")
            today = datetime.now()

            # Check for old date
            if (today - date).days > 365:
                self.flags.append("old_date")

            # Check for recent date
            if (today - date).days <= 30:
                self.flags.append("recent_date")

            # Check for future date
            if (date - today).days > 30:
                self.flags.append("future_date")

        except (ValueError, TypeError):
            pass

    def get_results(self) -> dict[str, Any]:
        """Get interview results."""
        return {
            "answers": self.answers,
            "flags": list(set(self.flags)),  # Remove duplicates
            "completed": self.is_complete(),
        }

    def is_complete(self) -> bool:
        """Check if interview is complete."""
        return not self.current_id
