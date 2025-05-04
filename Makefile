.PHONY: setup interview lint clean sync

setup:
	@echo "📦 Setting up environment..."
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

interview:
	@echo "🎤 Running CLI interview..."
	.venv/bin/python cli/main.py

lint:
	@echo "🔍 Linting code..."
	.venv/bin/flake8 cli backend

clean:
	@echo "🧹 Cleaning build files and interview logs..."
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -delete
	find . -name '*.txt' -delete

sync:
	@echo "☁️ Syncing with GitHub..."
	@bash ./SyncMyMac2OnlineGit.sh


