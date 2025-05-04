.PHONY: setup interview lint clean sync test

setup:
	@echo "📦 Setting up environment..."
	PYTHONPATH=$(PWD) python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	@echo "📦 Installing package in development mode..."
	PYTHONPATH=$(PWD) .venv/bin/pip install -e .

interview:
	@echo "🎤 Running CLI interview..."
	PYTHONPATH=$(PWD) .venv/bin/python cli/main.py

lint:
	@echo "🔍 Linting code..."
	PYTHONPATH=$(PWD) .venv/bin/flake8 cli backend

test:
	@echo "🧪 Running tests..."
	PYTHONPATH=$(PWD) .venv/bin/pytest tests/ -v

clean:
	@echo "🧹 Cleaning build files and interview logs..."
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -delete
	find . -name '*.txt' -delete

sync:
	@echo "☁️ Syncing with GitHub..."
	@bash ./SyncMyMac2OnlineGit.sh


