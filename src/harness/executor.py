"""Task executor following Ralph's autonomous loop pattern."""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from .task import Task, TaskStatus


class TaskExecutor:
    """Executes tasks in an autonomous loop similar to Ralph.

    This executor:
    - Loads tasks from tasks.json
    - Executes highest-priority incomplete tasks
    - Updates task status
    - Logs progress to progress.txt
    - Supports iteration limits
    """

    def __init__(
        self,
        tasks_file: Path = Path("tasks.json"),
        progress_file: Path = Path("progress.txt"),
        task_runner: Optional[Callable] = None,
    ):
        """Initialize the executor.

        Args:
            tasks_file: Path to tasks.json file
            progress_file: Path to progress.txt log file
            task_runner: Optional custom task runner function
        """
        self.tasks_file = tasks_file
        self.progress_file = progress_file
        self.task_runner = task_runner or self._default_task_runner
        self.tasks: list[Task] = []
        self.current_iteration = 0
        self.max_iterations = 10

    def load_tasks(self) -> None:
        """Load tasks from tasks.json."""
        if not self.tasks_file.exists():
            raise FileNotFoundError(f"Tasks file not found: {self.tasks_file}")

        with open(self.tasks_file) as f:
            data = json.load(f)

        self.max_iterations = data.get("metadata", {}).get("max_iterations", 10)
        self.current_iteration = data.get("metadata", {}).get("current_iteration", 0)

        # Convert JSON tasks to Task objects
        self.tasks = []
        for task_data in data.get("tasks", []):
            # Create a simple wrapper function that the task runner will call
            task = Task(
                name=task_data["title"],
                func=self.task_runner,
                kwargs={
                    "task_data": task_data,
                },
            )
            # Store original data for later use
            task.task_data = task_data
            task.priority = task_data.get("priority", 999)

            # Set initial status based on passes field
            if task_data.get("passes", False):
                task.status = TaskStatus.SUCCESS
                task.result = "Previously completed"

            self.tasks.append(task)

    def save_tasks(self) -> None:
        """Save current task state back to tasks.json."""
        with open(self.tasks_file) as f:
            data = json.load(f)

        # Update task completion status
        for task in self.tasks:
            task_data = task.task_data
            for json_task in data["tasks"]:
                if json_task["id"] == task_data["id"]:
                    json_task["passes"] = task.status == TaskStatus.SUCCESS
                    break

        # Update metadata
        data["metadata"]["current_iteration"] = self.current_iteration

        with open(self.tasks_file, "w") as f:
            json.dump(data, f, indent=2)

    def log_progress(self, message: str) -> None:
        """Append a message to progress.txt.

        Args:
            message: The progress message to log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.progress_file, "a") as f:
            f.write(f"\n[{timestamp}] Iteration {self.current_iteration}\n")
            f.write(f"{message}\n")

    def get_next_task(self) -> Optional[Task]:
        """Get the highest-priority incomplete task.

        Returns:
            The next task to execute, or None if all complete
        """
        incomplete_tasks = [
            task for task in self.tasks
            if not task.is_complete and task.status != TaskStatus.SUCCESS
        ]

        if not incomplete_tasks:
            return None

        # Sort by priority (lower number = higher priority)
        incomplete_tasks.sort(key=lambda t: t.priority)
        return incomplete_tasks[0]

    def _default_task_runner(self, task_data: dict) -> Any:
        """Default task runner for demonstration purposes.

        Args:
            task_data: The task data dictionary from tasks.json

        Returns:
            Task result
        """
        import random

        duration = task_data.get("duration_seconds", 1)
        should_fail = task_data.get("should_fail", False)

        # Simulate work with progress updates
        steps = 10
        for i in range(steps):
            time.sleep(duration / steps)
            # Progress updates would be handled by the TUI

        if should_fail:
            raise Exception(f"Task {task_data['id']} failed as configured")

        return f"Completed {task_data['id']}"

    async def _default_task_runner_async(self, task_data: dict) -> Any:
        """Async version of default task runner.

        Args:
            task_data: The task data dictionary from tasks.json

        Returns:
            Task result
        """
        import random

        duration = task_data.get("duration_seconds", 1)
        should_fail = task_data.get("should_fail", False)

        # Simulate work with progress updates
        steps = 10
        for i in range(steps):
            await asyncio.sleep(duration / steps)

        if should_fail:
            raise Exception(f"Task {task_data['id']} failed as configured")

        return f"Completed {task_data['id']}"

    async def execute_task(self, task: Task) -> None:
        """Execute a single task.

        Args:
            task: The task to execute
        """
        task.start()

        try:
            # Check if task function is async
            if asyncio.iscoroutinefunction(task.func):
                result = await task.func(**task.kwargs)
            else:
                # Run sync function in executor to avoid blocking
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: task.func(**task.kwargs))

            task.complete(result)
            self.log_progress(f"✓ Completed: {task.name}")
        except Exception as e:
            error_msg = str(e)
            task.fail(error_msg)
            self.log_progress(f"✗ Failed: {task.name} - {error_msg}")

    async def run_iteration(self) -> bool:
        """Run a single iteration of the loop.

        Returns:
            True if there are more tasks to process, False if complete
        """
        self.current_iteration += 1

        task = self.get_next_task()
        if not task:
            self.log_progress("All tasks completed!")
            return False

        self.log_progress(f"Starting task: {task.name}")
        await self.execute_task(task)
        self.save_tasks()

        return True

    async def run(self) -> None:
        """Run the autonomous loop until completion or max iterations."""
        self.load_tasks()

        while self.current_iteration < self.max_iterations:
            has_more = await self.run_iteration()
            if not has_more:
                break

        if self.current_iteration >= self.max_iterations:
            self.log_progress(f"Reached maximum iterations ({self.max_iterations})")
