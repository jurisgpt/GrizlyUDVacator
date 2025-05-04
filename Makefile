.PHONY: setup interview lint clean sync test analyze docs coverage smoke

# Setup environment
setup:
	@echo "📦 Setting up environment..."
	PYTHONPATH=$(PWD) python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt
	@echo "📦 Installing package in development mode..."
	PYTHONPATH=$(PWD) .venv/bin/pip install -e .

# Run CLI interview
interview:
	@echo "🎤 Running CLI interview..."
	PYTHONPATH=$(PWD) .venv/bin/python cli/main.py

# Code quality checks
lint:
	@echo "🔍 Running code quality checks..."
	@echo "🔍 Flake8..."
	PYTHONPATH=$(PWD) .venv/bin/flake8 cli backend
	@echo "🔍 Pylint..."
	PYTHONPATH=$(PWD) .venv/bin/pylint cli backend
	@echo "🔍 Mypy..."
	PYTHONPATH=$(PWD) .venv/bin/mypy cli backend
	@echo "🔍 Black formatting..."
	PYTHONPATH=$(PWD) .venv/bin/black --check cli backend
	@echo "🔍 Isort..."
	PYTHONPATH=$(PWD) .venv/bin/isort --check cli backend

smoke:
	@echo "🔥 Running smoke tests with coverage..."
	PYTHONPATH=$(PWD) .venv/bin/coverage run --source=grizlyudvacator -m pytest tests/smoke/ -v
	PYTHONPATH=$(PWD) .venv/bin/coverage report -m --include=grizlyudvacator/*

test:
	@echo "🧪 Running tests..."
	PYTHONPATH=$(PWD) .venv/bin/pytest tests/ -v --cov=cli --cov=backend

# Code complexity analysis
analyze:
	@echo "📊 Running code complexity analysis..."
	@echo "📊 Cyclomatic Complexity..."
	PYTHONPATH=$(PWD) .venv/bin/radon cc -a -nc cli backend
	@echo "📊 Maintainability Index..."
	PYTHONPATH=$(PWD) .venv/bin/radon mi -s cli backend
	@echo "📊 Raw metrics..."
	PYTHONPATH=$(PWD) .venv/bin/radon raw cli backend

docs:
	@echo "📚 Building documentation..."
	PYTHONPATH=$(PWD) .venv/bin/sphinx-build -b html docs/ docs/_build/html

coverage:
	@echo "📊 Generating coverage report..."
	PYTHONPATH=$(PWD) .venv/bin/coverage html
	PYTHONPATH=$(PWD) .venv/bin/coverage report -m

clean:
	@echo "🧹 Cleaning build files and interview logs..."
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -delete
	find . -name '*.txt' -delete
	find . -name '*.log' -delete
	sudo rm -rf .venv/
	sudo rm -rf .pytest_cache/
	sudo rm -rf .mypy_cache/
	sudo rm -rf .coverage
	sudo rm -rf htmlcov/
	sudo rm -rf docs/_build/

sync:
	@echo "☁️ Syncing with GitHub..."
	@bash ./SyncMyMac2OnlineGit.sh
