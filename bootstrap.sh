#!/bin/bash

echo "🔧 Setting up GrizlyUDVacator environment..."

# Step 1: Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Step 2: Install dependencies
pip install -r requirements.txt

echo "✅ Setup complete. Virtual environment activated."
echo "👉 To re-activate later: source .venv/bin/activate"
