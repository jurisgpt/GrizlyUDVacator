#!/usr/bin/env bash

# Improved ASP Test Runner for GrizlyUDVacator
# ----------------------------------------------

# Exit immediately if a command exits with a non-zero status
set -e

# Set color variables for better output readability
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Display header with formatting
echo -e "${BLUE}====================================${NC}"
echo -e "${BLUE}Running ASP Test Suite for GrizlyUDVacator${NC}"
echo -e "${BLUE}====================================${NC}"

# Define the ASP engine with parameters
MAIN_ASP_FILE="$(pwd)/scripts/solvers/asp/ud_vacate.asp"
TEST_DIR="$(pwd)/scripts/solvers/asp/tests"
ENGINE="/opt/homebrew/bin/clingo $MAIN_ASP_FILE"
FAIL_COUNT=0
TOTAL_COUNT=0
FAILED_TESTS=()
TEST_STATS=()

# Debug output
echo "Main ASP file: $MAIN_ASP_FILE"
echo "Test directory: $TEST_DIR"

# Check if test directory exists
if [ ! -d "$TEST_DIR" ]; then
    echo -e "${RED}Error: Test directory $TEST_DIR does not exist${NC}"
    exit 1
fi

# Check if test files exist
if [ -z "$(ls -A $TEST_DIR/*.asp 2>/dev/null)" ]; then
    echo -e "${YELLOW}Warning: No test files found in $TEST_DIR${NC}"
    exit 0
fi

# Process each test file
for testfile in $TEST_DIR/*.asp; do
    TOTAL_COUNT=$((TOTAL_COUNT + 1))
    TEST_NAME=$(basename "$testfile")
    START_TIME=$(date +%s%N)

    echo -ne "${BLUE}→ Testing ${TEST_NAME}...${NC} "

    # Extract predicates from #show directives
    PREDICATES=$(grep '#show' "$testfile" | sed 's/#show //g' | sed 's/\.$//g')

    # Skip test if no predicates found
    if [ -z "$PREDICATES" ]; then
        echo -e "${YELLOW}⚠️  Skipping - no predicates to check${NC}"
        continue
    fi

    # Run the test with timeout protection and capture execution time
    START_EXEC=$(date +%s%N)
    TEST_FILE="$TEST_DIR/$TEST_NAME"
    echo "Running test: $TEST_FILE"
    echo "Main ASP file: $MAIN_ASP_FILE"

    # Debug: Try running clingo directly
    if ! /opt/homebrew/bin/clingo "$MAIN_ASP_FILE" "$TEST_FILE" --quiet=1; then
        echo -e "${RED}Error running clingo: $?${NC}"
        echo "Command: /opt/homebrew/bin/clingo $MAIN_ASP_FILE $TEST_FILE --quiet=1"
    fi

    OUTPUT=$(timeout 10s /opt/homebrew/bin/clingo "$MAIN_ASP_FILE" "$TEST_FILE" --quiet=1 2>/dev/null)
    END_EXEC=$(date +%s%N)
    EXEC_TIME=$((($END_EXEC-$START_EXEC)/1000000)) # Convert to milliseconds

    # Extract rule definitions for analysis
    RULES=$(grep -A 3 'rule(' "$testfile" | grep -v '#test' | grep -v '#show')

    # Check if all predicates are present
    MISSING_PREDICATES=false
    MISSING_COUNT=0
    TOTAL_PREDICATES=0

    for PREDICATE in $PREDICATES; do
        TOTAL_PREDICATES=$((TOTAL_PREDICATES + 1))
        if ! echo "$OUTPUT" | grep -q "$PREDICATE"; then
            MISSING_PREDICATES=true
            MISSING_COUNT=$((MISSING_COUNT + 1))
        fi
    done

    if [ "$MISSING_PREDICATES" = false ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        TEST_STATS+=("${TEST_NAME}: PASS, ${EXEC_TIME}ms, ${TOTAL_PREDICATES} predicates")
    else
        echo -e "${RED}✗ FAIL${NC}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAILED_TESTS+=("$TEST_NAME")
        TEST_STATS+=("${TEST_NAME}: FAIL, ${EXEC_TIME}ms, ${TOTAL_PREDICATES} predicates (${MISSING_COUNT} missing)")

        # Display detailed diagnostics
        echo -e "${YELLOW}  Test Analysis:${NC}"
        echo -e "  ${CYAN}Execution time:${NC} ${EXEC_TIME}ms"
        echo -e "  ${CYAN}Total predicates:${NC} ${TOTAL_PREDICATES}"
        echo -e "  ${CYAN}Missing predicates:${NC} ${MISSING_COUNT}"

        echo -e "${YELLOW}  Expected predicates:${NC}"
        for PREDICATE in $PREDICATES; do
            if ! echo "$OUTPUT" | grep -q "$PREDICATE"; then
                echo -e "  ${RED}✗ $PREDICATE${NC}"
            else
                echo -e "  ${GREEN}✓ $PREDICATE${NC}"
            fi
        done

        echo -e "${YELLOW}  Rule Analysis:${NC}"
        echo "$RULES" | while read -r line; do
            echo -e "  ${CYAN}$line${NC}"
        done

        echo -e "${YELLOW}  Actual output (first 5 lines):${NC}"
        echo "$OUTPUT" | head -n 5 | while read -r line; do
            echo -e "  ${NC}$line${NC}"
        done
        echo ""
    fi
done

echo -e "${BLUE}====================================${NC}"
echo -e "Tests completed: $TOTAL_COUNT"

# Display summary with statistics
echo -e "${BLUE}Test Summary:${NC}"
echo -e "${BLUE}------------------------------------${NC}"
echo -e "${GREEN}✓ Passed:${NC} $((TOTAL_COUNT - FAIL_COUNT))"
echo -e "${RED}✗ Failed:${NC} $FAIL_COUNT"

# Display detailed test statistics
echo -e "${BLUE}------------------------------------${NC}"
echo -e "${BLUE}Test Statistics:${NC}"
echo -e "${BLUE}------------------------------------${NC}"
for stat in "${TEST_STATS[@]}"; do
    echo -e "${CYAN}$stat${NC}"
done

# Display summary
if [ "$FAIL_COUNT" -ne 0 ]; then
    echo -e "${BLUE}------------------------------------${NC}"
    echo -e "${RED}⚠️  $FAIL_COUNT test(s) failed:${NC}"
    for failed in "${FAILED_TESTS[@]}"; do
        echo -e "  ${RED}✗ $failed${NC}"
    done
    echo -e "${BLUE}====================================${NC}"
    exit 1
else
    echo -e "${BLUE}------------------------------------${NC}"
    echo -e "${GREEN}✅ All $TOTAL_COUNT tests passed successfully.${NC}"
    echo -e "${BLUE}====================================${NC}"
    exit 0
fi
