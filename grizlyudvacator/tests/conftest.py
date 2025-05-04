import logging
import os
import sys
import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# Get absolute path to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Ensure project root is in Python path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Add all necessary directories to Python path
for dir_name in ["backend", "cli", "tests"]:
    dir_path = os.path.join(PROJECT_ROOT, dir_name)
    if os.path.exists(dir_path) and dir_path not in sys.path:
        sys.path.insert(0, dir_path)

# Print Python path for debugging
print("\nPython path:")
for path in sys.path:
    print(path)
print("\n")

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Performance monitoring threshold (in seconds)
PERFORMANCE_THRESHOLD = 2.0

# Test configuration
TEST_CONFIG = {
    "paths": {
        "data_dir": os.path.join(os.path.dirname(__file__), "data"),
        "output_dir": os.path.join(os.path.dirname(__file__), "output"),
        "fixtures_dir": os.path.join(os.path.dirname(__file__), "fixtures"),
    },
    "settings": {"max_retries": 3, "timeout": 5, "debug": True},
}


# Mock external services
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == "http://test-api.example.com/data":
        return MockResponse({"status": "ok", "data": []}, 200)
    return MockResponse({}, 404)


# Environment setup
@pytest.fixture(autouse=True)
def set_test_environment():
    """Set up test environment."""
    # Set environment variables
    os.environ["TESTING"] = "true"
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DEBUG"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["CACHE_ENABLED"] = "false"
    os.environ["DATABASE_URL"] = "test-db-url"

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create test directories
    test_dirs = [
        TEST_CONFIG["paths"]["data_dir"],
        TEST_CONFIG["paths"]["output_dir"],
        TEST_CONFIG["paths"]["fixtures_dir"],
        "tests/tmp",
        "tests/data",
    ]

    for dir_path in test_dirs:
        os.makedirs(dir_path, exist_ok=True)
        logger.debug(f"Created test directory: {dir_path}")


# Mock external services
@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock external services for all tests."""
    with patch("requests.get", side_effect=mocked_requests_get):
        yield


# Performance monitoring
@pytest.fixture(autouse=True)
def monitor_performance():
    """Monitor test execution time."""
    start_time = time.time()
    test_name = os.environ.get("PYTEST_CURRENT_TEST", "unknown").split(" ")[0]

    yield

    end_time = time.time()
    duration = end_time - start_time

    if duration > PERFORMANCE_THRESHOLD:
        logger.warning(
            f"Test {test_name} took {duration:.2f}s - potential performance issue"
        )
    else:
        logger.debug(f"Test {test_name} completed in {duration:.2f}s")


# Test configuration
@pytest.fixture(autouse=True)
def test_config():
    """Provide test configuration."""
    return TEST_CONFIG


# Test isolation
@pytest.fixture(autouse=True)
def isolate_tests():
    """Isolate tests by resetting state."""
    # Reset global state
    if hasattr(sys, "modules"):
        for module in list(sys.modules.keys()):
            if module.startswith("backend.") or module.startswith("cli."):
                del sys.modules[module]

    # Clear caches
    if hasattr(sys, "path_importer_cache"):
        sys.path_importer_cache.clear()

    # Reset mocks
    patch.stopall()

    yield

    # Additional cleanup
    patch.stopall()


# Clean up test environment
@pytest.fixture(autouse=True)
def cleanup_test_environment():
    """Clean up test environment after each test."""
    yield

    # Clean up test directories
    test_dirs = [TEST_CONFIG["paths"]["output_dir"], "tests/tmp", "tests/data"]

    for dir_path in test_dirs:
        if os.path.exists(dir_path):
            for file_name in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logger.debug(f"Cleaned up file: {file_path}")
                except Exception as e:
                    logger.error(f"Error cleaning up {file_path}: {str(e)}")


# Additional utility fixtures
@pytest.fixture
def test_timestamp():
    """Provide a consistent timestamp for tests."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


@pytest.fixture
def test_data_dir():
    """Provide test data directory path."""
    return TEST_CONFIG["paths"]["data_dir"]


@pytest.fixture
def test_output_dir():
    """Provide test output directory path."""
    return TEST_CONFIG["paths"]["output_dir"]
