import os
import shutil
from pathlib import Path


def move_files():
    # Move backend files
    backend_files = list(Path("backend").glob("**/*"))
    for file in backend_files:
        if file.is_file():
            rel_path = file.relative_to("backend")
            target_path = Path("grizlyudvacator/backend") / rel_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(target_path))

    # Move cli files
    cli_files = list(Path("cli").glob("**/*"))
    for file in cli_files:
        if file.is_file():
            rel_path = file.relative_to("cli")
            target_path = Path("grizlyudvacator/cli") / rel_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(target_path))

    # Move test files
    test_files = list(Path("tests").glob("**/*"))
    for file in test_files:
        if file.is_file():
            rel_path = file.relative_to("tests")
            target_path = Path("grizlyudvacator/tests") / rel_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(target_path))


if __name__ == "__main__":
    move_files()
