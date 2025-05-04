#!/usr/bin/env python3
"""
Default Judgment Interview System
For Legal Aid Intake Coordinators

This script implements a structured interview system for tenant intake
when assessing the viability of a motion to set aside default judgment
in eviction cases.
"""

import datetime
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from grizlyudvacator.cli.interview.interview_engine import InterviewEngine
from grizlyudvacator.cli.io.console_io import ConsoleIO
from grizlyudvacator.cli.io.io_interface import IOInterface


def load_yaml(path: str) -> dict[str, Any]:
    """Load YAML file from the given path."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
            # Validate basic structure
            if not isinstance(data, dict) or "questions" not in data:
                raise ValueError("Invalid YAML structure: missing questions section")
            return data
    except Exception as e:
        print(f"❌ Failed to load YAML: {e}")
        sys.exit(1)


def _ask_question_impl(io: IOInterface, q: dict[str, Any]) -> Any:
    """Internal implementation of ask_question that uses IO interface."""
    io.write_output(f"\n❓ {q['prompt']}")

    # Handle question options and default
    if "options" in q:
        io.write_output("Options: " + ", ".join(q["options"]))
    if "default" in q:
        io.write_output(f"Default: {q['default']}")

    # Handle different question types
    if q["type"] == "text":
        return io.read_input("Your answer: ").strip()
    elif q["type"] == "number":
        while True:
            try:
                return float(io.read_input("Enter a number: ").strip())
            except ValueError:
                io.write_output("Please enter a valid number.")
    elif q["type"] == "summary":
        io.write_output("📋 Interview complete. Thank you!")
        return None
    elif q["type"] == "boolean":
        while True:
            ans = io.read_input("Enter [y/n]: ").strip().lower()
            if ans in ["y", "yes"]:
                return True
            elif ans in ["n", "no"]:
                return False
            else:
                io.write_output("Please enter y or n.")
    elif q["type"] == "choice":
        for i, opt in enumerate(q["options"]):
            io.write_output(f"{i+1}. {opt}")
        while True:
            sel = io.read_input("Enter choice number: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(q["options"]):
                return q["options"][int(sel) - 1]
            else:
                io.write_output("Invalid choice.")
    elif q["type"] == "date":
        while True:
            date_str = io.read_input("Enter date (YYYY-MM-DD): ").strip()
            try:
                # Validate date format
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
                return date_str
            except ValueError:
                io.write_output("Invalid date format. Please use YYYY-MM-DD.")
    elif q["type"] == "multiple_choice":
        selected = []
        for i, opt in enumerate(q["options"]):
            io.write_output(f"{i+1}. {opt}")
        io.write_output("Enter numbers separated by commas, or 'done' when finished")
        while True:
            sel = io.read_input("Selection: ").strip()
            if sel.lower() == "done":
                break
            try:
                choices = [int(x.strip()) for x in sel.split(",")]
                for choice in choices:
                    if (
                        1 <= choice <= len(q["options"])
                        and q["options"][choice - 1] not in selected
                    ):
                        selected.append(q["options"][choice - 1])
                io.write_output(f"Current selections: {', '.join(selected)}")
            except ValueError:
                io.write_output("Invalid input. Enter numbers separated by commas.")
        return selected
    else:
        io.write_output(f"⚠️ Unsupported question type: {q['type']}")
        return None


def _run_interview_impl(io: IOInterface, yaml_data):
    """Internal implementation of run_interview that uses IO interface."""
    # Initialize interview engine
    engine = InterviewEngine(yaml_data)
    answers = {}
    flags = []
    current_id = engine.current_id

    while current_id:
        question = engine.get_question(current_id)
        ans = _ask_question_impl(io, question)
        answers[current_id] = ans

        # Process flags and next question
        if question.follow_up:
            if isinstance(ans, bool):
                branch = "if_true" if ans else "if_false"
                next_info = question.follow_up.get(branch, {})
                flags.extend(next_info.get("flags", []))
                current_id = next_info.get("next", question.get("next"))
            elif isinstance(ans, str) and "options" in question.follow_up:
                next_info = question.follow_up["options"].get(ans, {})
                flags.extend(next_info.get("flags", []))
                current_id = next_info.get("next", question.get("next"))
            else:
                current_id = question.get("next")
        else:
            current_id = question.get("next")

        # Handle text-based flags
        if question.flags_from_text and isinstance(ans, str):
            # Get the keywords section
            keywords = question.flags_from_text.get("keywords", [])
            if isinstance(keywords, list):
                # If it's a list, convert to dict format
                keywords_dict = {}
                for item in keywords:
                    if isinstance(item, dict) and len(item) == 1:
                        key = next(iter(item))
                        value = item[key]
                        keywords_dict[key] = value
                keywords = keywords_dict

            # Now process the keywords
            for label, pattern in keywords.items():
                if re.search(rf"\b{pattern}\b", ans, re.IGNORECASE):
                    flags.append(label)

            # Calculate time-based flags if dates are involved
            if question.type == "date" and question.date_flags and ans:
                try:
                    date_obj = datetime.datetime.strptime(ans, "%Y-%m-%d").date()
                    today = datetime.date.today()
                    days_diff = (today - date_obj).days

                    for flag, threshold in question.date_flags.items():
                        if days_diff >= threshold:
                            flags.append(flag)
                except ValueError:
                    # Skip if date is invalid
                    pass

    # Generate recommendation based on flags
    io.write_output("\n📝 Initial Assessment:")
    if "improper_service" in flags:
        io.write_output(
            " ✅ Potential grounds for motion based on improper service (CCP § 473.5)"
        )
    if "mistake_neglect" in flags:
        io.write_output(
            " ✅ Potential grounds based on mistake/excusable neglect (CCP § 473(b))"
        )
    if "fraud_misconduct" in flags:
        io.write_output(" ✅ Potential grounds based on fraud/misconduct (CCP § 473(d))")
    if "void_judgment" in flags:
        io.write_output(" ✅ Potential void judgment argument available")
    if "time_barred" in flags:
        io.write_output(" ⚠️ Motion may be time-barred - careful review needed")
    if "urgent_lockout" in flags:
        io.write_output(" ⚠️ URGENT: Lockout imminent - consider ex parte application")

    if not any(
        x in flags
        for x in [
            "improper_service",
            "mistake_neglect",
            "fraud_misconduct",
            "void_judgment",
        ]
    ):
        io.write_output(
            " ⚠️ No clear grounds for relief identified - further review needed"
        )

    return answers, flags

    return answers


def save_results(
    answers: dict[str, Any],
    flags: list[str],
    save_path: str | None = None,
    io: IOInterface | None = None,
) -> bool:
    """Save interview results to a text file.

    For backward compatibility, this function can be called in two ways:
    1. save_results(answers, flags, save_path) - uses default ConsoleIO
    2. save_results(answers, flags, save_path, io) - uses provided IO interface
    """
    if io is None:
        io = ConsoleIO()

    if not save_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"interview_results_{timestamp}.txt"

    # Format results
    result_text = "Interview Results\n" + "=" * 20 + "\n\n"
    result_text += "Answers:\n" + "-" * 20 + "\n"
    for q_id, answer in answers.items():
        result_text += f"{q_id}: {answer}\n"

    result_text += "\nFlags:\n" + "-" * 20 + "\n"
    for flag in flags:
        result_text += f"{flag}\n"

    # Save to file
    io.write_file(save_path, result_text)
    return True


class InterviewRunner:
    """Class to manage interview execution.

    Attributes:
        yaml_data (Dict[str, Any]): YAML data containing interview questions and logic
        io (Optional[IOInterface]): Optional IO interface for user interaction
        engine (InterviewEngine): Interview engine instance
    """

    def __init__(self, yaml_data: dict[str, Any], io: IOInterface | None = None):
        """Initialize with YAML data and optional IO interface.

        Args:
            yaml_data (Dict[str, Any]): YAML data containing interview questions and logic
            io (Optional[IOInterface]): Optional IO interface for user interaction
        """
        self.yaml_data = yaml_data
        self.io = io or ConsoleIO()
        self.engine = InterviewEngine(yaml_data)

    def run(self) -> dict[str, Any]:
        """Run the interview and return results.

        Returns:
            Dict[str, Any]: Dictionary containing user answers and flags
        """
        current_id = self.yaml_data.get(
            "start_id", self.yaml_data["questions"][0]["id"]
        )

        while True:
            question = self.engine.get_question(current_id)
            if not question:
                break

            current_id = self._ask_question(question)
            if current_id is None:
                break

        answers = self.engine.get_answers()
        flags = self.engine.get_flags()

        return answers, flags

    def _ask_question(self, question: dict[str, Any]) -> Any:
        """Ask a question and return the answer.

        Args:
            question (Dict[str, Any]): Dictionary containing question details

        Returns:
            The user's answer to the question or None for summary questions
        """
        while True:
            try:
                if "prompt" in question:
                    self.io.write_output(f"\n❓ {question['prompt']}")

                # Handle question options and default
                if "options" in question:
                    self.io.write_output("Options: " + ", ".join(question["options"]))
                if "default" in question:
                    self.io.write_output(f"Default: {question['default']}")

                # Handle different question types
                if question["type"] == "text":
                    answer = self.io.read_input("Your answer: ").strip()
                elif question["type"] == "number":
                    while True:
                        try:
                            answer = float(
                                self.io.read_input("Enter a number: ").strip()
                            )
                            break
                        except ValueError:
                            self.io.write_output("Please enter a valid number.")
                elif question["type"] == "summary":
                    self.io.write_output("\n📊 INTERVIEW SUMMARY")
                    self.io.write_output("🧾 Collected Answers:")
                    answers = self.engine.get_answers()
                    for key, value in answers.items():
                        if key == "has_children":
                            value = "Yes" if value else "No"
                        self.io.write_output(f"  - {key}: {value}")
                    return None
                elif question["type"] == "boolean":
                    self.io.write_output(f"\n❓ {question['prompt']}\n\nEnter [y/n]:")
                    while True:
                        ans = self.io.read_input(" ").strip().lower()
                        if ans in ["y", "yes"]:
                            answer = True
                            break
                        elif ans in ["n", "no"]:
                            answer = False
                            break
                        else:
                            self.io.write_output("Please enter y or n.")
                elif question["type"] == "choice":
                    for i, opt in enumerate(question["options"]):
                        self.io.write_output(f"{i+1}. {opt}")
                    while True:
                        sel = self.io.read_input("Enter choice number: ").strip()
                        if sel.isdigit() and 1 <= int(sel) <= len(question["options"]):
                            answer = question["options"][int(sel) - 1]
                            break
                        else:
                            self.io.write_output("Please enter a valid choice number.")
                elif question["type"] == "date":
                    while True:
                        date_str = self.io.read_input(
                            "Enter date (YYYY-MM-DD): "
                        ).strip()
                        try:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                            today = date.today()
                            if date_obj > today:
                                self.io.write_output("Date cannot be in the future")
                                continue
                            answer = date_str
                            break
                        except ValueError:
                            self.io.write_output(
                                "Invalid date format. Please use YYYY-MM-DD."
                            )
                elif question["type"] == "multiple_choice":
                    selected = []
                    for i, opt in enumerate(question["options"]):
                        self.io.write_output(f"{i+1}. {opt}")
                    self.io.write_output(
                        "Enter numbers separated by commas, or 'done' when finished"
                    )
                    while True:
                        sel = self.io.read_input("Selection: ").strip()
                        if sel.lower() == "done":
                            break
                        try:
                            choices = [int(x.strip()) for x in sel.split(",")]
                            for choice in choices:
                                if (
                                    1 <= choice <= len(question["options"])
                                    and question["options"][choice - 1] not in selected
                                ):
                                    selected.append(question["options"][choice - 1])
                            self.io.write_output(
                                f"Current selections: {', '.join(selected)}"
                            )
                        except ValueError:
                            self.io.write_output(
                                "Invalid input. Enter numbers separated by commas."
                            )
                    answer = selected
                else:
                    self.io.write_output(
                        f"⚠️ Unsupported question type: {question['type']}"
                    )
                    continue

                # Process the answer and get next question ID
                try:
                    next_id = self.engine.process_answer(question["id"], answer)
                    return next_id
                except ValueError as e:
                    self.io.write_output(str(e))
                    continue
            except ValueError as e:
                self.io.write_output(str(e))
                continue


def run_interview(
    yaml_data: dict[str, Any], io: IOInterface | None = None
) -> dict[str, Any]:
    """Run an interview using the provided YAML data and optional IO interface."""
    runner = InterviewRunner(yaml_data, io)
    return runner.run()


def main(args=None):
    # Initialize IO
    io = ConsoleIO()

    # Get YAML path
    yaml_path = io.join_path(
        os.path.dirname(__file__), "prompts", "vacate_default.yaml"
    )
    if not io.exists(yaml_path):
        io.write_output(f"❌ Error: YAML file not found at {yaml_path}")
        sys.exit(1)

    yaml_data = load_yaml(yaml_path)

    # Run the interview
    answers, flags = run_interview(io, yaml_data)

    # Evaluate legal basis
    result = evaluate_statutes(flags)

    # Generate the motion document
    generate_motion(answers, result)

    # Ask if the user wants to save plain-text results
    save = input("\nSave results to file? [y/n]: ").strip().lower()
    if save in ["y", "yes"]:
        save_results(answers, flags)

    print("\n👋 Thank you for using the Default Judgment Interview System.")


if __name__ == "__main__":
    main()
