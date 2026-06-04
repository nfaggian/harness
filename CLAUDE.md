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
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Running the Harness

```bash
# Run with default files (tasks.json, progress.txt)
python3 -m harness.cli

# Or if installed
harness

# Run with custom task file
python3 -m harness.cli --tasks my-tasks.json

# Run with custom progress log
python3 -m harness.cli --progress logs/progress.txt
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
- `duration_seconds`: Example field for demo tasks
- `should_fail`: Example field for testing error handling

## Ralph Pattern Implementation

Following Ralph's autonomous loop approach:

1. **Task Selection**: Executor picks highest-priority incomplete task (`passes: false`)
2. **Execution**: Runs task with progress tracking
3. **Persistence**: Updates `tasks.json` with completion status
4. **Logging**: Appends learnings to `progress.txt`
5. **Iteration**: Repeats until all complete or max iterations reached
6. **Fresh Context**: Each task execution is independent (though currently in same process)

Unlike Ralph's bash script spawning fresh AI instances, this harness runs tasks in-process but maintains the same conceptual model of iterative, tracked execution.

## Extending the Harness

### Custom Task Runners

The default task runner is a demo implementation. To use custom task logic:

```python
from harness import TaskExecutor

def my_task_runner(task_data: dict):
    # Your custom task execution logic
    # Access task_data fields like task_data["id"], etc.
    result = do_work(task_data)
    return result

executor = TaskExecutor(task_runner=my_task_runner)
```

### Adding New Task Fields

Tasks are loaded from JSON and passed to the task runner. Add any fields you need to `tasks.json` and access them via `task_data` in your runner function.
