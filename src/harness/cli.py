"""Command-line interface for the harness."""

import argparse
import sys
import traceback
from pathlib import Path

from .tui import run_tui


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Harness - Task execution framework with TUI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default files (tasks.json and progress.txt in current directory)
  harness

  # Run with custom task file
  harness --tasks my-tasks.json

  # Run with custom progress log
  harness --progress logs/progress.txt

  # Run with both custom files
  harness --tasks my-tasks.json --progress logs/progress.txt
        """,
    )

    parser.add_argument(
        "--tasks",
        type=Path,
        default=Path("tasks.json"),
        help="Path to tasks.json file (default: tasks.json)",
    )

    parser.add_argument(
        "--progress",
        type=Path,
        default=Path("progress.txt"),
        help="Path to progress.txt log file (default: progress.txt)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="harness 0.1.0",
    )

    args = parser.parse_args()

    # Check if tasks file exists
    if not args.tasks.exists():
        print(f"Error: Tasks file not found: {args.tasks}", file=sys.stderr)
        print("\nCreate a tasks.json file with the following structure:", file=sys.stderr)
        print(
            """
{
  "tasks": [
    {
      "id": "task-1",
      "title": "Example Task",
      "description": "Task description",
      "priority": 1,
      "passes": false
    }
  ],
  "metadata": {
    "max_iterations": 10,
    "current_iteration": 0
  }
}
        """,
            file=sys.stderr,
        )
        sys.exit(1)

    # Ensure progress file exists
    args.progress.parent.mkdir(parents=True, exist_ok=True)
    if not args.progress.exists():
        args.progress.write_text("# Progress Log\n\n---\n")

    # Run the TUI
    try:
        run_tui(tasks_file=args.tasks, progress_file=args.progress)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
