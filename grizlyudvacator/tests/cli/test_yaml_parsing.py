import pytest

from grizlyudvacator.cli.io.console_io import ConsoleIO
from grizlyudvacator.cli.io.io_interface import IOInterface
from grizlyudvacator.cli.main import load_yaml


@pytest.fixture
def test_io():
    class TestIO(IOInterface):
        def __init__(self):
            self.files = {}

        def read_input(self, prompt: str) -> str:
            return ""

        def write_output(self, message: str) -> None:
            pass

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


def test_load_valid_yaml(test_io):
    """Test loading valid YAML."""
    yaml_content = """
questions:
  - id: q1
    type: boolean
    prompt: Test question
  - id: q2
    type: text
    prompt: Another question
"""

    io = TestIO()
    io.files["test.yaml"] = yaml_content

    result = load_yaml("test.yaml", io)
    assert isinstance(result, dict)
    assert len(result["questions"]) == 2
    assert result["questions"][0]["id"] == "q1"
    assert result["questions"][1]["id"] == "q2"


def test_load_invalid_yaml():
    """Test loading invalid YAML."""
    yaml_content = """
questions:
  - id: q1
    type: boolean
    prompt: Test question
  - # Invalid question
    prompt: Another question
"""

    io = TestIO()
    io.files["test.yaml"] = yaml_content

    with pytest.raises(ValueError):
        load_yaml("test.yaml", io)


def test_load_missing_questions_section():
    """Test loading YAML without questions section."""
    yaml_content = """
version: 1.0
author: Test
"""

    io = TestIO()
    io.files["test.yaml"] = yaml_content

    with pytest.raises(ValueError):
        load_yaml("test.yaml", io)


def test_load_empty_file():
    """Test loading empty YAML file."""
    io = TestIO()
    io.files["test.yaml"] = ""

    with pytest.raises(ValueError):
        load_yaml("test.yaml", io)


def test_load_nonexistent_file():
    """Test loading non-existent file."""
    io = TestIO()

    with pytest.raises(FileNotFoundError):
        load_yaml("nonexistent.yaml", io)


def test_load_yaml_with_flags():
    """Test loading YAML with flags."""
    yaml_content = """
questions:
  - id: q1
    type: boolean
    prompt: Test question
    flags:
      - flag1
      - flag2
  - id: q2
    type: text
    prompt: Another question
    flags_from_text:
      keywords:
        - emergency: emergency
        - urgent: urgent
"""

    io = TestIO()
    io.files["test.yaml"] = yaml_content

    result = load_yaml("test.yaml", io)
    assert result["questions"][0]["flags"] == ["flag1", "flag2"]
    assert result["questions"][1]["flags_from_text"]["keywords"] == [
        {"emergency": "emergency"},
        {"urgent": "urgent"},
    ]


def test_load_yaml_with_follow_up():
    """Test loading YAML with follow-up logic."""
    yaml_content = """
questions:
  - id: q1
    type: boolean
    prompt: Test question
    follow_up:
      if_true:
        next: q2
        flags:
          - true_flag
      if_false:
        next: q3
        flags:
          - false_flag
  - id: q2
    type: text
    prompt: Follow-up if true
  - id: q3
    type: text
    prompt: Follow-up if false
"""

    io = TestIO()
    io.files["test.yaml"] = yaml_content

    result = load_yaml("test.yaml", io)
    assert result["questions"][0]["follow_up"]["if_true"]["next"] == "q2"
    assert result["questions"][0]["follow_up"]["if_false"]["next"] == "q3"
    assert result["questions"][0]["follow_up"]["if_true"]["flags"] == ["true_flag"]
    assert result["questions"][0]["follow_up"]["if_false"]["flags"] == ["false_flag"]
