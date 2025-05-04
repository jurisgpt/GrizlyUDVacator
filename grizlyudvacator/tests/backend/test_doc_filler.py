import glob
import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from grizlyudvacator.backend.generator.doc_filler import (
    generate_motion,
    generate_summary_md,
)


def test_generate_summary_md_creates_file():
    # Prepare dummy answers and result data
    answers = {
        "Did you receive a summons?": "No",
        "When did you first learn of the judgment?": "2024-12-01",
    }
    result = {
        "statutes": ["CCP § 473(b)", "CCP § 473.5"],
        "justification": {
            "CCP § 473(b)": ["Excusable neglect", "Mistake of fact"],
            "CCP § 473.5": ["No actual notice", "Timely motion"],
        },
    }

    # Before generating, capture existing .md files
    existing_md_files = set(glob.glob("cli/summary_*.md"))

    # Call the function
    output_path = generate_summary_md(answers, result)

    # Afterward, check for new .md file
    new_md_files = set(glob.glob("cli/summary_*.md")) - existing_md_files
    assert len(new_md_files) == 1, "No new summary markdown file created"
    assert output_path is not None
    assert output_path.endswith(".md")
    assert "summary_" in output_path

    # Cleanup: Optionally remove the file to keep test output clean
    for f in new_md_files:
        os.remove(f)


def test_generate_motion_with_missing_template():
    """Test that generate_motion handles missing template file gracefully"""
    # Create dummy answers and result
    answers = {"test": "value"}
    result = {
        "statutes": ["CCP § 473(b)"],
        "justification": {"CCP § 473(b)": ["Excusable neglect"]},
    }

    # Temporarily rename the template directory to simulate missing template
    os.rename("backend/generator/templates", "backend/generator/templates_backup")

    try:
        # This should raise FileNotFoundError
        output_path = generate_motion(answers, result)
        assert output_path is None
    finally:
        # Restore the templates directory
        os.rename("backend/generator/templates_backup", "backend/generator/templates")


def test_generate_motion_with_invalid_template():
    """Test that generate_motion handles invalid template file gracefully"""
    # Create dummy answers and result
    answers = {"test": "value"}
    result = {
        "statutes": ["CCP § 473(b)"],
        "justification": {"CCP § 473(b)": ["Excusable neglect"]},
    }

    # Create an invalid template file
    template_path = "backend/generator/templates/motion_template.docx"
    with open(template_path, "w") as f:
        f.write("invalid docx content")

    try:
        # This should fail because the file is not a valid DOCX
        output_path = generate_motion(answers, result)
        assert output_path is None
    finally:
        # Clean up the invalid template
        os.remove(template_path)


def teardown_module():
    """Clean up generated test files"""
    import glob

    for file in glob.glob("cli/summary_*.md"):
        os.remove(file)
