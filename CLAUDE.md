# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Harness is a task execution framework with a TUI (Text User Interface) that follows the Ralph autonomous loop pattern. It allows you to define tasks in a JSON file and execute them iteratively while tracking progress visually.

Inspired by [snarktank/ralph](https://github.com/snarktank/ralph), this harness provides:
- Task execution in priority order
- Visual progress tracking via TUI
- Iteration-based execution loops
- Progress logging
- Task status persistence

## Architecture

### Core Components

**Task Management** (`src/harness/task.py`)
- `Task` dataclass: Represents a single executable task with status tracking
- `TaskStatus` enum: States (PENDING, RUNNING, SUCCESS, FAILED, CANCELLED)
- Progress tracking, timing, and error handling

**Executor** (`src/harness/executor.py`)
- `TaskExecutor`: Implements Ralph-style autonomous loop
- Loads tasks from `tasks.json`
- Executes highest-priority incomplete tasks
- Logs progress to `progress.txt`
- Supports max iteration limits

**TUI** (`src/harness/tui.py`)
- Built with [Textual](https://textual.textualize.io/)
- Real-time task status visualization
- Progress bars and statistics
- Interactive controls (Run, Pause, Clear Log, Quit)
- Widgets:
  - `TaskProgressWidget`: Current task execution
  - `IterationStatsWidget`: Iteration and task counters
  - `TaskListWidget`: All tasks with status icons
  - `ProgressLogWidget`: Scrolling event log

**CLI** (`src/harness/cli.py`)
- Entry point for running the harness
- Argument parsing for custom task/progress files

### File Structure

```
harness/
├── tasks.json              # Task definitions (like Ralph's prd.json)
├── progress.txt            # Append-only progress log
├── src/harness/
│   ├── __init__.py
│   ├── task.py            # Task data models
│   ├── executor.py        # Execution engine
│   ├── tui.py             # TUI interface
│   └── cli.py             # CLI entry point
├── pyproject.toml         # Python package config
└── requirements.txt       # Dependencies
```

## Development Commands

### Setup

**Using uv (recommended):**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
make install
# or: uv pip install -r requirements.txt

# Install with dev dependencies
make dev-install
# or: uv pip install -e ".[dev]"
```

**Traditional method:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Makefile Commands

```bash
make help          # Show all available commands
make install       # Install dependencies with uv
make dev-install   # Install with dev dependencies
make clean         # Remove build artifacts
make lint          # Run ruff linting
make format        # Format code with ruff
make run           # Run with default tasks.json
make run-gemini    # Run with tasks-gemini.json
make run-shell     # Run with tasks-shell.json
make check-gemini  # Verify gemini-cli installation
```

### Running the Harness

```bash
# Using Make
make run
make run-gemini  # Requires gemini-cli
make run-shell

# Direct execution
python3 -m harness.cli
python3 -m harness.cli --tasks my-tasks.json
python3 -m harness.cli --progress logs/progress.txt

# With uv
uv run python -m harness.cli
```

### TUI Controls

- `r` or "Run" button: Start execution loop
- `p` or "Pause" button: Pause execution
- `c` or "Clear Log" button: Clear the progress log view
- `q` or "Quit" button: Exit the application

## Task File Format

The `tasks.json` file follows this structure:

```json
{
  "tasks": [
    {
      "id": "unique-task-id",
      "title": "Human-readable task name",
      "description": "Task description",
      "priority": 1,
      "passes": false,
      "duration_seconds": 3,
      "should_fail": false
    }
  ],
  "metadata": {
    "created": "2026-06-04",
    "max_iterations": 10,
    "current_iteration": 0
  }
}
```

**Key Fields:**
- `id`: Unique identifier
- `title`: Display name (shown in TUI)
- `priority`: Lower numbers execute first
- `passes`: Boolean tracking completion (like Ralph's prd.json)
- `runner`: Task runner type ("gemini", "shell", or omit for default)

**Runner-specific fields:**

For default runner:
- `duration_seconds`: Simulated task duration
- `should_fail`: Force task failure for testing

For gemini runner:
- `prompt`: The prompt to send to Gemini CLI
- `auto_approve`: Auto-approve Gemini actions (default: false)
- `json_output`: Request JSON output (default: false)

For shell runner:
- `command`: Shell command to execute
- `timeout`: Command timeout in seconds (default: 300)

## Ralph Pattern Implementation

Following Ralph's autonomous loop approach:

1. **Task Selection**: Executor picks highest-priority incomplete task (`passes: false`)
2. **Execution**: Runs task with progress tracking
3. **Persistence**: Updates `tasks.json` with completion status
4. **Logging**: Appends learnings to `progress.txt`
5. **Iteration**: Repeats until all complete or max iterations reached
6. **Fresh Context**: Each task execution is independent (though currently in same process)

Unlike Ralph's bash script spawning fresh AI instances, this harness runs tasks in-process but maintains the same conceptual model of iterative, tracked execution.

## Task Runners

Harness supports pluggable task runners:

### Built-in Runners

1. **Default Runner**: Demo/testing runner with simulated delays
2. **Gemini Runner** (`src/harness/runners/gemini_runner.py`): Executes tasks via gemini-cli
3. **Shell Runner** (`src/harness/runners/shell_runner.py`): Executes shell commands

### Using Runners

Specify the runner in task JSON:
```json
{"runner": "gemini", "prompt": "...", ...}
{"runner": "shell", "command": "...", ...}
{} // No runner field = default runner
```

### Custom Task Runners

Add your own runner:

```python
from harness import TaskExecutor

def my_runner(task_data: dict):
    # Your custom logic
    result = do_work(task_data)
    return result

executor = TaskExecutor()
executor.runners['myrunner'] = my_runner
```

Then use it:
```json
{"runner": "myrunner", "id": "task-1", ...}
```

## Gemini CLI Integration

Install gemini-cli for AI-powered tasks:
```bash
npm install -g @google/gemini-cli

# Verify installation
make check-gemini
```

Example Gemini task:
```json
{
  "id": "analyze-code",
  "title": "Code Analysis",
  "runner": "gemini",
  "prompt": "Review src/harness/task.py and suggest improvements",
  "priority": 1,
  "passes": false
}
```

## Package Management with uv

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management.

**Why uv:**
- 10-100x faster than pip
- Deterministic dependency resolution
- Built-in virtual environment management
- Drop-in replacement for pip

**Common uv commands:**
```bash
uv pip install package-name
uv pip install -r requirements.txt
uv pip install -e .
uv run python script.py
```
