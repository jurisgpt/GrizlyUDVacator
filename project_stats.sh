#!/bin/bash
echo "📊 Project Statistics for GrizlyUDVacator"
echo "📁 Directory: $(pwd)"
echo "🕐 Date: $(date)"

echo ""
echo "📂 Total directories:"
find . -type d | wc -l

echo ""
echo "📄 Total files:"
find . -type f | wc -l

echo ""
echo "🧾 Python files count:"
find . -name "*.py" | wc -l

echo ""
echo "📄 Lines of code in Python files:"
find . -name "*.py" | xargs wc -l

echo ""
echo "📊 Language breakdown using cloc:"
which cloc > /dev/null
if [ $? -eq 0 ]; then
  cloc .
else
  echo "❗ 'cloc' not found. Install with: brew install cloc"
fi

echo ""
echo "🧠 Cyclomatic complexity using radon:"
which radon > /dev/null
if [ $? -eq 0 ]; then
  radon cc . -s -a
else
  echo "❗ 'radon' not found. Install with: pip install radon"
fi
