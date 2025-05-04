import os
from pathlib import Path


def get_project_root() -> Path:
    """Get the root directory of the project."""
    return Path(__file__).parent.parent.parent


def get_output_dir() -> Path:
    """Get the output directory for generated files."""
    output_dir = get_project_root() / "output" / "documents"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_template_dir() -> Path:
    """Get the directory containing template files."""
    return get_project_root() / "backend" / "generator" / "templates"


def get_fixture_dir() -> Path:
    """Get the directory containing test fixtures."""
    return get_project_root() / "tests" / "fixtures"
