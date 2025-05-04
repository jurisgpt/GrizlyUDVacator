import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import z3

from grizlyudvacator.formal.interview_model import InterviewVerifier


class Z3ProofLogger:
    def __init__(self, output_dir: str = "logs"):
        """Initialize the logger with output directory."""
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent
        self.output_dir = project_root / output_dir
        self.verifier = InterviewVerifier()
        os.makedirs(self.output_dir, exist_ok=True)

    def create_test_case(self, days_ago: int, flags: dict[str, int]) -> dict[str, Any]:
        """Create a test case with specified days ago and flags."""
        current_date = datetime.now()
        answer_date = current_date - timedelta(days=days_ago)
        return {
            "answer_date": answer_date.isoformat(),
            "current_date": current_date.isoformat(),
            "flags": flags,
        }

    def evaluate_flags(self, test_case: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate flags using Z3 and return detailed results.

        Returns:
            Dict containing:
            - status: SAT/UNSAT
            - z3_model: Z3 model if SAT
            - z3_constraints: Generated Z3 constraints
            - triggered_flags: List of triggered flags
            - explanation: Detailed analysis
        """
        current_date = datetime.fromisoformat(test_case["current_date"])
        answer_date = datetime.fromisoformat(test_case["answer_date"])
        flags = test_case["flags"]

        # Create Z3 solver and variables
        solver = z3.Solver()
        current = z3.Int("current")
        answer = z3.Int("answer")

        # Add base constraints
        solver.add(current == int(current_date.timestamp()))
        solver.add(answer == int(answer_date.timestamp()))

        # Add flag constraints
        constraints = []
        for threshold, days in flags.items():
            threshold_ts = answer_date.timestamp() + (days * 24 * 60 * 60)
            constraint = z3.Implies(current > threshold_ts, z3.Bool(threshold))
            solver.add(constraint)
            constraints.append(str(constraint))

        # Check and get model
        result = solver.check()
        model = solver.model() if result == z3.sat else None

        # Generate explanation
        explanation = []
        for threshold, days in flags.items():
            threshold_ts = answer_date.timestamp() + (days * 24 * 60 * 60)
            current_ts = current_date.timestamp()
            if current_ts > threshold_ts:
                explanation.append(
                    f"Flag '{threshold}' triggered (current: {current_ts}, threshold: {threshold_ts})"
                )
            else:
                explanation.append(
                    f"Flag '{threshold}' not triggered (current: {current_ts}, threshold: {threshold_ts})"
                )

        return {
            "status": "SAT" if result == z3.sat else "UNSAT",
            "z3_model": str(model) if model else "None",
            "z3_constraints": constraints,
            "triggered_flags": [
                flag
                for flag, days in flags.items()
                if current_date.timestamp()
                > (answer_date.timestamp() + (days * 24 * 60 * 60))
            ],
            "explanation": explanation,
            "current_date": current_date.isoformat(),
            "answer_date": answer_date.isoformat(),
            "flags": flags,
            "timestamp": datetime.now().isoformat(),
        }

    def log_proof(
        self,
        test_case: dict[str, Any],
        result: dict[str, Any],
        format: str = "markdown",
    ) -> None:
        """Log the Z3 proof in specified format."""
        # Ensure logs directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        if format == "markdown":
            log = f"""
### [{result['timestamp']}]: Test Case - {test_case["answer_date"]} vs {test_case["current_date"]}

📅 Current Date: {result["current_date"]}
📅 Answer Date: {result["answer_date"]}

⚠️ Flags:
{json.dumps(result["flags"], indent=2)}

🧠 Z3 Status: `{result["status"]}`

✅ Triggered Flags: {', '.join(result["triggered_flags"])}

🔍 Detailed Analysis:
{chr(10).join(f"- {item}" for item in result["explanation"])}

📝 Z3 Model:
```
{result['z3_model']}
```

📋 Z3 Constraints:
```
{chr(10).join(result['z3_constraints'])}
```

---
"""

            # Write markdown log
            with open(self.output_dir / "z3_proof_log.md", "a") as f:
                f.write(log)

        elif format == "json":
            # Ensure JSON log file exists and is properly formatted
            json_file = self.output_dir / "z3_proof_log.json"

            # Create file with empty list if it doesn't exist
            if not json_file.exists():
                with open(json_file, "w") as f:
                    json.dump([], f)

            # Read existing data
            try:
                with open(json_file) as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = []

            # Add new result
            data.append(result)

            # Write back with proper formatting
            try:
                with open(json_file, "w") as f:
                    json.dump(data, f, indent=2)
                print(f"Logged result to {json_file}")
            except Exception as e:
                print(f"Error writing JSON: {e}")
                # If writing fails, try to append the result as a new line
                try:
                    with open(json_file, "a") as f:
                        f.write(json.dumps(result, indent=2) + "\n")
                    print(f"Appended result to {json_file}")
                except Exception as e:
                    print(f"Error appending to JSON: {e}")


def run_verification_suite():
    """Run a suite of verification tests."""
    logger = Z3ProofLogger()

    # Define comprehensive test cases
    test_cases = [
        # Case 1: Multiple thresholds triggered
        logger.create_test_case(
            days_ago=10,
            flags={
                "urgent": 7,
                "warning": 14,
                "info": 30,
                "critical": 5,
                "important": 21,
            },
        ),
        # Case 2: No thresholds triggered
        logger.create_test_case(
            days_ago=1, flags={"urgent": 7, "warning": 14, "info": 30, "critical": 5}
        ),
        # Case 3: Edge case - exactly at threshold
        logger.create_test_case(days_ago=7, flags={"urgent": 7, "critical": 5}),
        # Case 4: Multiple thresholds with different days
        logger.create_test_case(
            days_ago=15,
            flags={
                "urgent": 7,
                "warning": 14,
                "info": 30,
                "critical": 5,
                "important": 21,
                "notice": 60,
            },
        ),
        # Case 5: All thresholds triggered
        logger.create_test_case(
            days_ago=65,
            flags={
                "urgent": 7,
                "warning": 14,
                "info": 30,
                "critical": 5,
                "important": 21,
                "notice": 60,
                "emergency": 3,
            },
        ),
        # Case 6: No thresholds (control case)
        logger.create_test_case(
            days_ago=3,
            flags={
                "urgent": 7,
                "warning": 14,
                "info": 30,
                "critical": 5,
                "important": 21,
                "notice": 60,
                "emergency": 3,
            },
        ),
        # Case 7: Multiple edge cases
        logger.create_test_case(
            days_ago=7,
            flags={
                "urgent": 7,
                "warning": 14,
                "info": 30,
                "critical": 5,
                "important": 21,
                "notice": 60,
                "emergency": 3,
            },
        ),
        # Case 8: Long-term thresholds
        logger.create_test_case(
            days_ago=90,
            flags={
                "urgent": 7,
                "warning": 14,
                "info": 30,
                "critical": 5,
                "important": 21,
                "notice": 60,
                "emergency": 3,
                "long_term": 90,
            },
        ),
    ]

    # Run and log each test case with both formats
    for i, case in enumerate(test_cases, 1):
        print(f"\nRunning Test Case {i}...")
        result = logger.evaluate_flags(case)
        logger.log_proof(case, result, format="markdown")
        logger.log_proof(case, result, format="json")


if __name__ == "__main__":
    run_verification_suite()
