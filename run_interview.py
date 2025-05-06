from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, TypeVar, Union

import yaml

from grizlyudvacator.cli.interview.interview_engine import InterviewEngine
from grizlyudvacator.cli.interview.legal_analysis import LegalAnalysis
from grizlyudvacator.cli.interview.legal_references import LegalReferences
from grizlyudvacator.cli.interview.question import Question
from grizlyudvacator.cli.io.console_io import ConsoleIO


def load_yaml(path: str) -> dict[str, Any]:
    """Load YAML file from the given path."""
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    # Initialize IO interface
    io = ConsoleIO()

    # Load YAML configuration
    yaml_path = (
        Path(__file__).parent / "grizlyudvacator/cli/prompts/vacate_default.yaml"
    )
    yaml_data = load_yaml(yaml_path)

    # Create interview engine
    engine = InterviewEngine(yaml_data, io)

    # Get current question
    question = engine.get_current_question()

    # Main interview loop
    while question:
        # Display question
        io.display(f"\n{question.prompt}")

        # Get answer based on question type
        if question.type == "text":
            answer = io.get_text()
        elif question.type == "number":
            answer = io.get_number()
        elif question.type == "boolean":
            answer = io.get_boolean()
        elif question.type == "date":
            answer = io.get_date()
        elif question.type == "choice":
            answer = io.get_choice(question.options)
        elif question.type == "multiple_choice":
            answer = io.get_multiple_choice(
                question.options, question.min_choices, question.max_choices
            )
        else:
            io.error(f"Unknown question type: {question.type}")
            break

        # Process answer
        try:
            next_id = engine.process_answer(question.id, answer)
            question = engine.get_current_question()
        except ValueError as e:
            io.error(f"Invalid answer: {str(e)}")
        except Exception as e:
            io.error(f"Error processing answer: {str(e)}")
            break

    # Interview complete
    io.display("\nInterview complete!")

    # Display results
    io.display("\nAnswers:")
    for q_id, answer in engine.sessions[engine.session_id]["answers"].items():
        io.display(f"- {q_id}: {answer}")

    io.display("\nFlags:")
    for flag in engine.sessions[engine.session_id]["flags"]:
        io.display(f"- {flag}")


if __name__ == "__main__":
    main()
