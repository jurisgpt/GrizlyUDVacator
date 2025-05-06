#!/usr/bin/env bash
set -e

# ----------------------------------------------------------------------------
# setup_asp_all.sh — Complete macOS setup for ASP & Z3 solvers, tests, and runner
# ----------------------------------------------------------------------------

echo
echo "=== Starting macOS environment setup for ASP & Z3 ==="

# 1. Ensure Homebrew
if ! command -v brew &> /dev/null; then
  echo "Homebrew not found. Installing..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "Homebrew already installed."
fi

# 2. Install Clingo & yq
echo "Installing Clingo and yq..."
brew install clingo yq

# 3. Install Z3 Python solver
echo "Installing Z3 Python solver via pip3..."
if command -v pip3 &> /dev/null; then
  pip3 install --user z3-solver
else
  echo "⚠️ pip3 not found: please install Python3 & pip."
fi

# 4. Scaffold solver directories
echo
echo "Creating solver directory structure..."
mkdir -p solvers/asp/tests
mkdir -p solvers/z3/models
mkdir -p solvers/z3/proofs

# 5. Copy core ASP engine
echo
echo "Populating ASP engine (ud_vacate.asp)..."
if [ ! -f solvers/asp/ud_vacate.asp ]; then
  cp ud_vacate.asp solvers/asp/
  echo " → Copied ud_vacate.asp"
else
  echo " → ud_vacate.asp already exists"
fi

# 6. Write test definitions YAML
echo
echo "Creating asp_tests.yaml..."
cat > solvers/asp/tests/asp_tests.yaml << 'EOF'
scenarios:
  - file: test_personal_service.asp
    facts:
      - personal_delivery(summons, complaint, defendant).
    expect: holds(service_complete(defendant))

  - file: test_substituted_service.asp
    facts:
      - not personal_delivery(summons, complaint, defendant).
      - reasonable_diligence_attempted(defendant).
    expect: holds(substituted_service_valid(defendant))

  - file: test_default_entry.asp
    facts:
      - not filed_pleading(defendant, complaint).
      - days_since_service_at_least(defendant, 30).
    expect: holds(clerk_enters_default(defendant))
EOF

# 7. Generate ASP test files
echo
echo "Generating ASP test files..."
pushd solvers/asp/tests > /dev/null
for scenario in $(yq e '.scenarios[].file' asp_tests.yaml); do
  facts=$(yq e ".scenarios[] | select(.file == \"$scenario\") | .facts[]" asp_tests.yaml)
  expect=$(yq e ".scenarios[] | select(.file == \"$scenario\") | .expect" asp_tests.yaml)
  echo " → $scenario"
  cat > "$scenario" << EOF
% $scenario — auto‑generated test for $expect
$facts
#show holds($expect).
EOF
done
popd > /dev/null

# 8. Create the test runner
echo
echo "Creating test runner script run_asp_tests.sh..."
cat > scripts/run_asp_tests.sh << 'EOF'
#!/usr/bin/env bash
set -e

echo "Running ASP test suite..."
ENGINE="clingo solvers/asp/ud_vacate.asp"
FAIL=0

for t in solvers/asp/tests/test_*.asp; do
  echo -n "Testing $t… "
  if $ENGINE "$t" --quiet=1 | grep -q 'holds('; then
    echo "OK"
  else
    echo "FAIL"
    FAIL=1
  fi
done

if [ "$FAIL" -ne 0 ]; then
  echo "🚨 Some tests failed!"
  exit 1
else
  echo "✅ All tests passed!"
  exit 0
fi
EOF
chmod +x scripts/run_asp_tests.sh

# 9. Final check
echo
echo "Setup complete. Here's what's in solvers/asp/tests/:"
ls solvers/asp/tests/

echo
echo "You can now run:  ./scripts/run_asp_tests.sh"
echo "=== macOS setup_asp_all.sh finished ==="
echo
