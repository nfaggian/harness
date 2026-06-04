"""TUI interface for the harness using Textual."""

import asyncio
from pathlib import Path
from typing import Optional

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Footer, Header, Label, ProgressBar, Static, Log
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel

from .executor import TaskExecutor
from .task import TaskStatus


class TaskProgressWidget(Static):
    """Widget showing current task progress."""

    current_task = reactive("")
    progress = reactive(0)
    status_message = reactive("")

    def render(self) -> Panel:
        """Render the current task progress."""
        if not self.current_task:
            content = Text("Waiting for tasks...", style="dim")
        else:
            content = Text()
            content.append(f"Current Task: ", style="bold cyan")
            content.append(f"{self.current_task}\n", style="white")

            if self.status_message:
                content.append(f"\n{self.status_message}", style="yellow")

            # Add progress bar
            bar_width = 40
            filled = int((self.progress / 100) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            content.append(f"\n\n[{bar}] {self.progress}%", style="green")

        return Panel(content, title="Current Execution", border_style="blue")


class IterationStatsWidget(Static):
    """Widget showing iteration statistics."""

    iteration = reactive(0)
    max_iterations = reactive(10)
    tasks_completed = reactive(0)
    tasks_failed = reactive(0)
    tasks_total = reactive(0)

    def render(self) -> Panel:
        """Render iteration stats."""
        content = Text()
        content.append(f"Iteration: ", style="bold")
        content.append(f"{self.iteration} / {self.max_iterations}\n", style="cyan")

        content.append(f"Tasks: ", style="bold")
        content.append(f"{self.tasks_completed} ", style="green")
        content.append(f"✓  ", style="green")
        content.append(f"{self.tasks_failed} ", style="red")
        content.append(f"✗  ", style="red")
        content.append(f"({self.tasks_total} total)", style="dim")

        return Panel(content, title="Statistics", border_style="green")


class TaskListWidget(Static):
    """Widget showing all tasks and their status."""

    def __init__(self, executor: TaskExecutor, **kwargs) -> None:
        """Initialize with task executor."""
        super().__init__(**kwargs)
        self.executor = executor

    def render(self) -> Panel:
        """Render the task list."""
        content = Text()

        if not self.executor.tasks:
            content.append("No tasks loaded", style="dim")
        else:
            for task in sorted(self.executor.tasks, key=lambda t: t.priority):
                # Status icon
                if task.status == TaskStatus.SUCCESS:
                    icon = "✓"
                    style = "green"
                elif task.status == TaskStatus.FAILED:
                    icon = "✗"
                    style = "red"
                elif task.status == TaskStatus.RUNNING:
                    icon = "▶"
                    style = "yellow"
                elif task.status == TaskStatus.CANCELLED:
                    icon = "⊘"
                    style = "dim"
                else:
                    icon = "○"
                    style = "dim"

                content.append(f"{icon} ", style=style)
                content.append(f"[P{task.priority}] ", style="cyan")
                content.append(f"{task.name}", style="white" if task.status != TaskStatus.SUCCESS else "dim")

                if task.error:
                    content.append(f" - {task.error}", style="red dim")

                content.append("\n")

        return Panel(content, title="Task Queue", border_style="cyan")


class ProgressLogWidget(VerticalScroll):
    """Widget showing the progress log."""

    def __init__(self, **kwargs) -> None:
        """Initialize the progress log widget."""
        super().__init__(**kwargs)
        self.log_widget = Log()

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield self.log_widget

    def add_line(self, message: str) -> None:
        """Add a line to the log.

        Args:
            message: The message to add
        """
        self.log_widget.write_line(message)


class HarnessApp(App):
    """Main TUI application for the harness."""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 3;
        grid-rows: auto 1fr auto;
    }

    #stats-container {
        column-span: 2;
        height: auto;
        layout: horizontal;
    }

    #task-progress {
        width: 2fr;
    }

    #iteration-stats {
        width: 1fr;
    }

    #task-list {
        column-span: 1;
        row-span: 1;
    }

    #progress-log {
        column-span: 1;
        row-span: 1;
        border: solid cyan;
        height: 100%;
    }

    #controls {
        column-span: 2;
        height: auto;
        layout: horizontal;
        padding: 1;
        background: $surface;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "run", "Run"),
        ("p", "pause", "Pause"),
        ("c", "clear_log", "Clear Log"),
    ]

    def __init__(self, tasks_file: Path = Path("tasks.json"), progress_file: Path = Path("progress.txt")):
        """Initialize the app.

        Args:
            tasks_file: Path to tasks.json
            progress_file: Path to progress.txt
        """
        super().__init__()
        self.executor = TaskExecutor(tasks_file, progress_file)
        self.running = False
        self.current_task_widget: Optional[TaskProgressWidget] = None
        self.stats_widget: Optional[IterationStatsWidget] = None
        self.task_list_widget: Optional[TaskListWidget] = None
        self.progress_log_widget: Optional[ProgressLogWidget] = None

    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        yield Header()

        with Container(id="stats-container"):
            self.current_task_widget = TaskProgressWidget(id="task-progress")
            yield self.current_task_widget

            self.stats_widget = IterationStatsWidget(id="iteration-stats")
            yield self.stats_widget

        self.task_list_widget = TaskListWidget(self.executor, id="task-list")
        yield self.task_list_widget

        self.progress_log_widget = ProgressLogWidget(id="progress-log")
        yield self.progress_log_widget

        with Horizontal(id="controls"):
            yield Button("Run", id="run-btn", variant="success")
            yield Button("Pause", id="pause-btn", variant="warning")
            yield Button("Clear Log", id="clear-btn")
            yield Button("Quit", id="quit-btn", variant="error")

        yield Footer()

    def on_mount(self) -> None:
        """Handle mount event."""
        self.title = "Harness - Task Execution TUI"
        self.sub_title = "Ralph-style autonomous loop"

        # Load tasks
        try:
            self.executor.load_tasks()
            self.update_stats()
            self.refresh_task_list()
            self.log_message("Tasks loaded successfully")
        except Exception as e:
            self.log_message(f"Error loading tasks: {e}", style="red")

    @on(Button.Pressed, "#run-btn")
    def action_run(self) -> None:
        """Start the execution loop."""
        if not self.running:
            self.running = True
            self.log_message("Starting execution loop...", style="green bold")
            self.run_loop()

    @on(Button.Pressed, "#pause-btn")
    def action_pause(self) -> None:
        """Pause the execution loop."""
        self.running = False
        self.log_message("Paused", style="yellow")

    @on(Button.Pressed, "#clear-btn")
    def action_clear_log(self) -> None:
        """Clear the progress log."""
        if self.progress_log_widget:
            self.progress_log_widget.log_widget.clear()

    @on(Button.Pressed, "#quit-btn")
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def log_message(self, message: str, style: str = "white") -> None:
        """Add a message to the progress log.

        Args:
            message: The message to log
            style: Rich style for the message (currently unused)
        """
        if self.progress_log_widget:
            self.progress_log_widget.add_line(message)

    def update_stats(self) -> None:
        """Update the statistics widget."""
        if self.stats_widget:
            self.stats_widget.iteration = self.executor.current_iteration
            self.stats_widget.max_iterations = self.executor.max_iterations
            self.stats_widget.tasks_total = len(self.executor.tasks)
            self.stats_widget.tasks_completed = sum(
                1 for t in self.executor.tasks if t.status == TaskStatus.SUCCESS
            )
            self.stats_widget.tasks_failed = sum(
                1 for t in self.executor.tasks if t.status == TaskStatus.FAILED
            )

    def refresh_task_list(self) -> None:
        """Refresh the task list display."""
        if self.task_list_widget:
            self.task_list_widget.refresh()

    @work(exclusive=True)
    async def run_loop(self) -> None:
        """Run the execution loop in the background."""
        while self.running and self.executor.current_iteration < self.executor.max_iterations:
            task = self.executor.get_next_task()
            if not task:
                self.log_message("All tasks completed! 🎉", style="green bold")
                self.running = False
                break

            # Update UI
            if self.current_task_widget:
                self.current_task_widget.current_task = task.name
                self.current_task_widget.progress = 0

            self.log_message(f"Starting: {task.name}", style="cyan")
            self.refresh_task_list()

            # Execute task with progress simulation
            task.start()
            self.refresh_task_list()

            try:
                # Simulate progress updates
                task_data = task.kwargs.get("task_data", {})
                duration = task_data.get("duration_seconds", 1)
                steps = 20

                for i in range(steps):
                    if not self.running:
                        self.log_message(f"Cancelled: {task.name}", style="yellow")
                        task.cancel()
                        break

                    await asyncio.sleep(duration / steps)

                    if self.current_task_widget:
                        self.current_task_widget.progress = int((i + 1) / steps * 100)

                if self.running:
                    # Actually execute the task
                    await self.executor.execute_task(task)

                    if task.status == TaskStatus.SUCCESS:
                        self.log_message(f"✓ Completed: {task.name}", style="green")
                    else:
                        self.log_message(f"✗ Failed: {task.name} - {task.error}", style="red")

            except Exception as e:
                self.log_message(f"✗ Error: {task.name} - {str(e)}", style="red")
                task.fail(str(e))

            self.executor.save_tasks()
            self.update_stats()
            self.refresh_task_list()

            # Small delay between tasks
            await asyncio.sleep(0.5)

        if self.executor.current_iteration >= self.executor.max_iterations:
            self.log_message(f"Reached max iterations ({self.executor.max_iterations})", style="yellow")
            self.running = False

        self.update_stats()


def run_tui(tasks_file: Path = Path("tasks.json"), progress_file: Path = Path("progress.txt")) -> None:
    """Run the TUI application.

    Args:
        tasks_file: Path to tasks.json
        progress_file: Path to progress.txt
    """
    app = HarnessApp(tasks_file, progress_file)
    app.run()
