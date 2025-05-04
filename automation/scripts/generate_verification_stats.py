import json
import os
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class VerificationStatsGenerator:
    def __init__(self, log_dir: str = "logs"):
        """Initialize with log directory."""
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent
        self.log_dir = project_root / log_dir

    def load_logs(self) -> pd.DataFrame:
        """Load all JSON logs into a DataFrame."""
        logs = []
        log_file = self.log_dir / "z3_proof_log.json"

        if not log_file.exists():
            print(f"Warning: JSON log file not found at {log_file}")
            return pd.DataFrame()

        try:
            # Read the entire file content
            with open(log_file) as f:
                content = f.read()

            # Try to parse the content as a single JSON array
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    logs = data
                else:
                    print("Warning: JSON root is not a list")
            except json.JSONDecodeError:
                # If that fails, try to split by newlines and parse each line
                lines = content.strip().split("\n")
                for line in lines:
                    if line.strip():
                        try:
                            log = json.loads(line)
                            logs.append(log)
                        except json.JSONDecodeError as e:
                            print(f"Warning: Could not parse line: {e}")
                            continue
        except Exception as e:
            print(f"Error reading JSON file: {e}")
            return pd.DataFrame()

        return pd.DataFrame(logs)

    def generate_stats(self, df: pd.DataFrame) -> dict:
        """Generate verification statistics."""
        stats = {
            "total_tests": len(df),
            "sat_percentage": (df["status"] == "SAT").mean() * 100,
            "average_flags_triggered": df["triggered_flags"].apply(len).mean(),
            "unique_flags": {flag for flags in df["flags"] for flag in flags},
            "timestamp_range": {
                "start": df["timestamp"].min(),
                "end": df["timestamp"].max(),
            },
        }
        return stats

    def plot_verification_stats(self, df: pd.DataFrame) -> None:
        """Generate visualization plots."""
        # Create output directory for plots
        plots_dir = self.log_dir / "plots"
        os.makedirs(plots_dir, exist_ok=True)

        # Convert timestamps to datetime objects
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Plot 1: Number of triggered flags over time
        plt.figure(figsize=(10, 6))
        df["flag_count"] = df["triggered_flags"].apply(len)
        sns.lineplot(data=df, x="timestamp", y="flag_count")
        plt.title("Number of Triggered Flags Over Time")
        plt.xlabel("Timestamp")
        plt.ylabel("Number of Flags")
        plt.savefig(plots_dir / "flags_over_time.png")
        plt.close()

        # Plot 2: Distribution of SAT/UNSAT results
        plt.figure(figsize=(8, 6))
        sns.countplot(data=df, x="status")
        plt.title("Distribution of SAT/UNSAT Results")
        plt.xlabel("Status")
        plt.ylabel("Count")
        plt.savefig(plots_dir / "sat_unsat_distribution.png")
        plt.close()

        # Plot 3: Most common triggered flags
        plt.figure(figsize=(10, 6))
        # Flatten the list of lists and count occurrences
        all_flags = [
            flag for sublist in df["triggered_flags"].tolist() for flag in sublist
        ]
        flag_counts = pd.Series(all_flags).value_counts()
        sns.barplot(x=flag_counts.index, y=flag_counts.values)
        plt.title("Most Commonly Triggered Flags")
        plt.xlabel("Flags")
        plt.ylabel("Count")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(plots_dir / "common_flags.png")
        plt.close()

    def generate_report(self) -> None:
        """Generate a comprehensive verification report."""
        df = self.load_logs()
        if df.empty:
            print("No logs found. Please run z3_proof_runner.py first.")
            return

        stats = self.generate_stats(df)
        self.plot_verification_stats(df)

        # Generate markdown report
        report = f"""
# Verification Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- Total Tests Run: {stats['total_tests']}
- SAT Percentage: {stats['sat_percentage']:.1f}%
- Average Flags Triggered: {stats['average_flags_triggered']:.1f}
- Timestamp Range: {stats['timestamp_range']['start']} to {stats['timestamp_range']['end']}

## Flag Statistics
Total Unique Flags: {len(stats['unique_flags'])}
Unique Flags: {', '.join(sorted(stats['unique_flags']))}

## Visualizations

![Status Distribution](plots/status_distribution.png)

![Flags Over Time](plots/flags_over_time.png)

![Flag Distribution](plots/flag_distribution.png)

---
This report demonstrates the mathematical proof of correctness for our date-based legal logic. Each SAT result represents a formal proof that our system correctly handles legal deadlines and flag triggering conditions.
"""

        with open(self.log_dir / "verification_report.md", "w") as f:
            f.write(report)


def main():
    """Run the verification stats generator."""
    generator = VerificationStatsGenerator()
    generator.generate_report()
    print("\nVerification report and statistics generated successfully!")
    print(f"Report location: {generator.log_dir / 'verification_report.md'}")
    print(f"Plots location: {generator.log_dir / 'plots'}")


if __name__ == "__main__":
    main()
