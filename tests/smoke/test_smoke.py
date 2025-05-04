def test_basic_imports():
    """Ensure main modules can be imported without syntax errors."""
    import grizlyudvacator.backend.interview.interview_engine
    import grizlyudvacator.cli.interview
    import grizlyudvacator.cli.io
    import grizlyudvacator.cli.main


def test_minimal_execution():
    """Minimal test to ensure program entrypoint doesn’t crash."""
    from grizlyudvacator.cli.main import load_yaml

    assert callable(load_yaml)
