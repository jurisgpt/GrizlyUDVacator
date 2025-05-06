#!/bin/bash

# Enhanced Test Runner for ASP Default Judgment Rules
# This script runs all enhanced test files and provides detailed analysis

# Directory containing the enhanced tests
TEST_DIR="$(dirname "$0")"
MAIN_ASP="${TEST_DIR}/../ud_vacate.asp"

# List of enhanced test files
TEST_FILES=(
    "test_excusable_neglect_enhanced.asp"
    "test_no_notice_enhanced.asp"
    "test_void_judgment_enhanced.asp"
    "test_improper_service_enhanced.asp"
)

# Debug levels
DEBUG_LEVEL=3  # 1=Basic, 2=Intermediate, 3=Detailed

# Function to run a single test
run_test() {
    local test_file="$1"
    local test_name="$(basename "$test_file" .asp)"

    echo "===================================="
    echo "Running Enhanced Test: $test_name"
    echo "===================================="
    echo "Main ASP file: $MAIN_ASP"
    echo "Test file: $test_file"
    echo "Debug Level: $DEBUG_LEVEL"

    # Run clingo with enhanced output
    /opt/homebrew/bin/clingo "$MAIN_ASP" "$test_file" --quiet=1 --stats

    # Capture and analyze results
    local result=$?
    local output=$(mktemp)
    /opt/homebrew/bin/clingo "$MAIN_ASP" "$test_file" --quiet=1 --stats > "$output"

    # Check for errors
    if [ $result -ne 0 ]; then
        echo "ERROR: Test failed to run"
        echo "=== Error Details ==="
        cat "$output"
        rm "$output"
        return 1
    fi

    # Analyze output
    echo "=== Test Analysis ==="
    echo "- Time Analysis:"
    grep -A 2 "Time:" "$output"
    echo "- Models:"
    grep -A 2 "Models:" "$output"
    echo "- Rule Analysis:"
    grep "vacate_default_judgment" "$output"

    rm "$output"
    return 0
}

# Function to analyze test results
analyze_results() {
    local test_file="$1"
    local test_name="$(basename "$test_file" .asp)"

    echo ""
    echo "=== Detailed Test Analysis: $test_name ==="

    # Check for specific warning patterns
    echo "- Warnings:"
    grep -i "warning" "$test_file"

    # Check for expected conclusions
    echo "- Expected Conclusions:"
    grep -i "vacate_default_judgment" "$test_file"

    # Check for time constraints
    echo "- Time Constraints:"
    grep -i "days_since" "$test_file"

    # Check for notice requirements
    echo "- Notice Requirements:"
    grep -i "notice" "$test_file"
}

# Main execution
PASS_COUNT=0
FAIL_COUNT=0
TOTAL_TESTS=${#TEST_FILES[@]}

echo "Starting Enhanced Test Suite"
echo "Total tests to run: $TOTAL_TESTS"
echo "Debug Level: $DEBUG_LEVEL"
echo ""

for test_file in "${TEST_FILES[@]}"; do
    echo ""
    echo "Running test: $test_file"

    if run_test "$TEST_DIR/$test_file"; then
        analyze_results "$TEST_DIR/$test_file"
        ((PASS_COUNT++))
        echo "✅ Test passed"
    else
        ((FAIL_COUNT++))
        echo "❌ Test failed"
    fi

    echo ""
    echo "------------------------------------"
    echo ""
done

# Final summary
echo ""
echo "=== Test Suite Summary ==="
echo "Total tests: $TOTAL_TESTS"
echo "Passed: $PASS_COUNT"
echo "Failed: $FAIL_COUNT"

# Detailed coverage analysis
echo ""
echo "=== Test Coverage Analysis ==="
echo "- Time Boundary Coverage:"
for test_file in "${TEST_FILES[@]}"; do
    test_name="$(basename "$test_file" .asp)"
    echo "  * $test_name:"
    grep -i "days" "$test_file" | wc -l
    echo ""
done

if [ $FAIL_COUNT -eq 0 ]; then
    echo ""
    echo "🎉 All enhanced tests passed successfully!"
else
    echo ""
    echo "❌ $FAIL_COUNT tests failed. Please review failed tests."
fi
