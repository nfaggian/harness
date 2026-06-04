.PHONY: help install dev-install clean test lint format run run-gemini run-shell

# Default target
help:
	@echo "Harness - Task Execution Framework"
	@echo ""
	@echo "Available targets:"
	@echo "  install        Install dependencies using uv"
	@echo "  dev-install    Install in development mode with dev dependencies"
	@echo "  clean          Remove build artifacts and cache files"
	@echo "  test           Run tests (when available)"
	@echo "  lint           Run code linting"
	@echo "  format         Format code with black"
	@echo "  run            Run harness with default tasks.json"
	@echo "  run-gemini     Run harness with gemini-cli tasks"
	@echo "  run-shell      Run harness with shell command tasks"
	@echo "  check-gemini   Check if gemini-cli is installed"

# Install dependencies using uv
install:
	@echo "Installing dependencies with uv..."
	uv pip install -r requirements.txt

# Install in development mode
dev-install:
	@echo "Installing in development mode with uv..."
	uv pip install -e ".[dev]"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage

# Run tests
test:
	@echo "Running tests..."
	uv run pytest tests/ -v

# Run linting
lint:
	@echo "Running linter..."
	uv run ruff check src/

# Format code
format:
	@echo "Formatting code..."
	uv run ruff format src/

# Run harness with default tasks
run:
	@echo "Running harness..."
	uv run python -m harness.cli

# Run harness with gemini-cli tasks
run-gemini:
	@echo "Running harness with gemini-cli tasks..."
	@if [ ! -f tasks-gemini.json ]; then \
		echo "Error: tasks-gemini.json not found"; \
		exit 1; \
	fi
	uv run python -m harness.cli --tasks tasks-gemini.json

# Run harness with shell tasks
run-shell:
	@echo "Running harness with shell tasks..."
	@if [ ! -f tasks-shell.json ]; then \
		echo "Error: tasks-shell.json not found"; \
		exit 1; \
	fi
	uv run python -m harness.cli --tasks tasks-shell.json

# Check if gemini-cli is installed
check-gemini:
	@echo "Checking for gemini-cli..."
	@if command -v gemini >/dev/null 2>&1; then \
		echo "✓ gemini-cli is installed"; \
		gemini --version; \
	else \
		echo "✗ gemini-cli not found"; \
		echo "Install it with: npm install -g @google/gemini-cli"; \
		exit 1; \
	fi
