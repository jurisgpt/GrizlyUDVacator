import subprocess
import os

# 🧪 Purpose:
# Test the CLI interview flow by running `cli/main.py` as a subprocess
# and verifying that it completes successfully and prints the expected output.

def test_interview_run():
    # 🗂️ Locate the main CLI script
    script_path = os.path.join("cli", "main.py")

    # 🚀 Launch the CLI script as if a user ran it from the terminal
    # - input=b"n\n": simulate the user typing 'n' (do not save file)
    # - capture stdout/stderr so we can inspect it
    result = subprocess.run(
        ["python3", script_path],
        input=b"n\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10  # 🛑 prevent hanging scripts
    )

    # 📤 Decode the output stream from bytes to string
    output = result.stdout.decode()

    # ✅ Validate that the program ran and reached the end
    assert "Thank you for using the Default Judgment Interview System" in output, \
        "Expected closing message not found in output"

    # ✅ Make sure it exited cleanly
    assert result.returncode == 0, f"Script exited with code {result.returncode}, stderr: {result.stderr.decode()}"


