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

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd harness

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running

```bash
# Run with default task file
python3 -m harness.cli

# Or with custom files
python3 -m harness.cli --tasks my-tasks.json --progress logs/progress.txt
```

### Creating Tasks

Create a `tasks.json` file:

```json
{
  "tasks": [
    {
      "id": "task-1",
      "title": "First Task",
      "description": "Description of the task",
      "priority": 1,
      "passes": false
    },
    {
      "id": "task-2",
      "title": "Second Task",
      "description": "Another task",
      "priority": 2,
      "passes": false
    }
  ],
  "metadata": {
    "max_iterations": 10,
    "current_iteration": 0
  }
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

## Customization

### Custom Task Runners

By default, tasks use a demo runner. To implement custom logic:

```python
from harness import TaskExecutor
from pathlib import Path

def my_task_runner(task_data: dict):
    # Your custom execution logic
    task_id = task_data["id"]
    # ... do work ...
    return result

executor = TaskExecutor(
    tasks_file=Path("tasks.json"),
    task_runner=my_task_runner
)
```

### Task Fields

Add any fields to your tasks in `tasks.json`:

```json
{
  "id": "build-project",
  "title": "Build Project",
  "priority": 1,
  "passes": false,
  "command": "npm run build",
  "timeout": 300,
  "custom_field": "value"
}
```

Access them in your task runner via `task_data["custom_field"]`.

## Inspired By

This project is inspired by [snarktank/ralph](https://github.com/snarktank/ralph), an autonomous AI agent loop. While Ralph spawns fresh AI instances for each iteration, Harness provides a general-purpose task execution framework with visual tracking.

## License

MIT
