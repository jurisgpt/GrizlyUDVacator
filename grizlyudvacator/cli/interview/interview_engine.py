import re
from datetime import datetime
from typing import Any, Dict, List, Optional


class InterviewEngine:
    """Core interview logic without I/O operations."""

    def __init__(self, yaml_data: dict[str, Any]):
        """Initialize with YAML data."""
        self.yaml_data = yaml_data
        self.questions = {q["id"]: q for q in yaml_data["questions"]}
        self.current_id = yaml_data.get("start_id", yaml_data["questions"][0]["id"])
        self.answers: dict[str, Any] = {}
        self.flags: list[str] = []

    def process_answer(self, question_id: str, answer: Any) -> str | None:
        """
        Process a question and its answer, returning the next question ID.

        Returns:
            str: ID of the next question, or None if interview is complete
        """
        q = self.questions[question_id]

        # Validate required fields
        if q.get("required") and not answer:
            return question_id  # Return same question ID to retry

        # Validate number ranges
        if q.get("type") == "number":
            if q.get("min") is not None and answer < q["min"]:
                return question_id  # Return same question ID to retry
            if q.get("max") is not None and answer > q["max"]:
                return question_id  # Return same question ID to retry

        self.answers[question_id] = answer

        # Capture static flags
        if "flags" in q:
            self.flags.extend(q["flags"])

        # Keyword-based flag detection using regex
        if q["type"] == "text" and "flags_from_text" in q and isinstance(answer, str):
            keywords = q["flags_from_text"].get("keywords", [])
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
        if q["type"] == "date" and "date_flags" in q and answer:
            try:
                date_obj = datetime.datetime.strptime(answer, "%Y-%m-%d").date()
                today = datetime.date.today()
                days_diff = (today - date_obj).days

                for flag, threshold in q["date_flags"].items():
                    if days_diff >= threshold:
                        self.flags.append(flag)
            except ValueError:
                pass

        # Determine next step
        if "follow_up" in q:
            if isinstance(answer, bool):
                branch = "if_true" if answer else "if_false"
                next_info = q["follow_up"].get(branch, {})
                self.flags.extend(next_info.get("flags", []))
                return next_info.get("next")
            elif isinstance(answer, str) and "options" in q["follow_up"]:
                next_info = q["follow_up"]["options"].get(answer, {})
                self.flags.extend(next_info.get("flags", []))
                return next_info.get("next", q.get("next"))
            else:
                return q.get("next")
        else:
            return q.get("next")

    def get_question(self, question_id: str) -> dict[str, Any]:
        """Get a question by ID."""
        return self.questions[question_id]

    def _get_next_question_id(
        self, question: dict[str, Any], answer: Any
    ) -> str | None:
        """Determine the next question ID based on the current question and answer."""
        # Capture static flags
        if "flags" in question:
            self.flags.extend(question["flags"])

        # Keyword-based flag detection using regex
        if (
            question["type"] == "text"
            and "flags_from_text" in question
            and isinstance(answer, str)
        ):
            keywords = question["flags_from_text"].get("keywords", [])
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
        if question["type"] == "date" and "date_flags" in question and answer:
            try:
                date_obj = datetime.strptime(answer, "%Y-%m-%d").date()
                today = date.today()
                days_diff = (today - date_obj).days

                for flag, threshold in question["date_flags"].items():
                    if days_diff >= threshold:
                        self.flags.append(flag)
            except ValueError:
                pass

        # Determine next step
        if "follow_up" in question:
            if isinstance(answer, bool):
                branch = "if_true" if answer else "if_false"
                next_info = question["follow_up"].get(branch, {})
                self.flags.extend(next_info.get("flags", []))
                return next_info.get("next")
            elif isinstance(answer, str) and "options" in question["follow_up"]:
                next_info = question["follow_up"]["options"].get(answer, {})
                self.flags.extend(next_info.get("flags", []))
                return next_info.get("next", question.get("next"))
            else:
                return question.get("next")
        else:
            return question.get("next")

    def get_answers(self) -> dict[str, Any]:
        """Get the collected answers."""
        return self.answers

    def get_flags(self) -> list[str]:
        """Get the triggered flags."""
        return list(set(self.flags))  # Remove duplicates

    def is_complete(self) -> bool:
        """Check if the interview is complete."""
        return self.current_id is None

    def get_current_question(self) -> dict[str, Any]:
        """Get the current question."""
        return self.questions[self.current_id] if self.current_id else None
