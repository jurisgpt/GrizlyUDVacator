#!/usr/bin/env bash
set -e

echo "Initializing solver directories..."

# Define directories to create
DIRS=(
  solvers/asp/tests
  solvers/z3/models
  solvers/z3/proofs
)

# Create each directory if it doesn't exist
echo "Creating directories: ${DIRS[*]}"
for dir in "${DIRS[@]}"; do
  mkdir -p "$dir"
  echo "  -> $dir"
done

# Ensure placeholder files exist
touch solvers/asp/ud_vacate.asp
touch solvers/z3/setup.py

echo "Bootstrap complete. Solver directories are ready!"
