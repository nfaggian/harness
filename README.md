# Harness

A task execution framework with TUI for easy tracking, inspired by [Ralph](https://github.com/snarktank/ralph).

## Features

- **Visual Task Tracking**: Real-time TUI built with [Textual](https://textual.textualize.io/)
- **Priority-based Execution**: Tasks run in priority order
- **Ralph Pattern**: Autonomous loop with iteration limits
- **Progress Logging**: Append-only log of execution events
- **Task Persistence**: JSON-based task state management
- **Interactive Controls**: Run, pause, and monitor tasks from the TUI

## Quick Start

### Prerequisites

- Python 3.10 or later
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- Optional: [gemini-cli](https://github.com/google-gemini/gemini-cli) for AI-powered tasks

### Installation

**Using uv (recommended):**
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/nfaggian/harness.git
cd harness

# Install dependencies
make install
# or: uv pip install -r requirements.txt
```

**Traditional pip:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Install gemini-cli (optional, for AI tasks):**
```bash
npm install -g @google/gemini-cli
```

### Running

**Using Make:**
```bash
# Run with default tasks
make run

# Run with gemini-cli tasks
make run-gemini

# Run with shell command tasks
make run-shell
```

**Direct execution:**
```bash
# Run with default task file
python3 -m harness.cli

# Or with custom files
python3 -m harness.cli --tasks my-tasks.json --progress logs/progress.txt
```

### Creating Tasks

Harness supports multiple task runners:

**1. Default Demo Runner** (`tasks.json`):
```json
{
  "tasks": [
    {
      "id": "demo-task",
      "title": "Demo Task",
      "description": "Simulated task execution",
      "priority": 1,
      "passes": false,
      "duration_seconds": 3
    }
  ],
  "metadata": {
    "max_iterations": 10,
    "current_iteration": 0
  }
}
```

**2. Gemini CLI Runner** (`tasks-gemini.json`):
```json
{
  "tasks": [
    {
      "id": "ai-task",
      "title": "AI Analysis",
      "description": "Use Gemini to analyze code",
      "priority": 1,
      "passes": false,
      "runner": "gemini",
      "prompt": "Analyze the codebase and suggest improvements",
      "auto_approve": false
    }
  ],
  "metadata": {"max_iterations": 10}
}
```

**3. Shell Command Runner** (`tasks-shell.json`):
```json
{
  "tasks": [
    {
      "id": "lint-task",
      "title": "Run Linter",
      "description": "Check code quality",
      "priority": 1,
      "passes": false,
      "runner": "shell",
      "command": "ruff check src/",
      "timeout": 60
    }
  ],
  "metadata": {"max_iterations": 10}
}
```

## TUI Interface

The TUI provides:

- **Current Task Panel**: Shows the active task with progress bar
- **Statistics Panel**: Displays iteration count and task completion stats
- **Task Queue**: Lists all tasks with status indicators (✓ = success, ✗ = failed, ▶ = running, ○ = pending)
- **Progress Log**: Scrolling log of execution events

### Controls

| Key | Action |
|-----|--------|
| `r` | Run/start execution loop |
| `p` | Pause execution |
| `c` | Clear log view |
| `q` | Quit application |

## Architecture

Harness follows the Ralph autonomous loop pattern:

1. Load tasks from `tasks.json`
2. Select highest-priority incomplete task (`passes: false`)
3. Execute task with progress tracking
4. Update task status in `tasks.json`
5. Log progress to `progress.txt`
6. Repeat until all tasks complete or max iterations reached

## Task Runners

Harness comes with three built-in task runners:

### 1. Default Runner
Simulates task execution with configurable duration and failure modes. Useful for testing.

### 2. Gemini CLI Runner
Executes tasks using Google's Gemini AI via gemini-cli. Perfect for AI-powered code analysis, generation, and automation.

**Task Fields:**
- `runner`: "gemini"
- `prompt`: The prompt to send to Gemini
- `auto_approve`: Auto-approve Gemini actions (default: false)
- `json_output`: Request JSON formatted output (default: false)

### 3. Shell Runner
Executes shell commands directly. Great for running builds, tests, linters, etc.

**Task Fields:**
- `runner`: "shell"
- `command`: Shell command to execute
- `timeout`: Command timeout in seconds (default: 300)

## Development

### Makefile Commands

```bash
make help          # Show all available commands
make install       # Install dependencies with uv
make dev-install   # Install with dev dependencies
make clean         # Remove build artifacts
make lint          # Run code linting
make format        # Format code with ruff
make run           # Run with default tasks
make run-gemini    # Run with gemini tasks
make run-shell     # Run with shell tasks
make check-gemini  # Verify gemini-cli is installed
```

## Customization

### Custom Task Runners

Add your own task runner:

```python
from harness import TaskExecutor
from pathlib import Path

def my_runner(task_data: dict):
    # Your custom logic
    return result

executor = TaskExecutor(tasks_file=Path("tasks.json"))
executor.runners['custom'] = my_runner
```

Then use it in tasks:
```json
{"runner": "custom", "id": "my-task", ...}
```

## Inspired By

This project is inspired by [snarktank/ralph](https://github.com/snarktank/ralph), an autonomous AI agent loop. While Ralph spawns fresh AI instances for each iteration, Harness provides a general-purpose task execution framework with visual tracking.

## License

MIT
