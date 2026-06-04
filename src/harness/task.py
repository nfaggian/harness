"""Task definitions and state management."""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from datetime import datetime


class TaskStatus(Enum):
    """Status of a task in the execution pipeline."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """A task to be executed by the harness.

    Attributes:
        name: Human-readable name for the task
        func: The callable to execute (can be sync or async)
        args: Positional arguments to pass to func
        kwargs: Keyword arguments to pass to func
        status: Current execution status
        result: Result of the task execution
        error: Error message if the task failed
        start_time: When the task started executing
        end_time: When the task finished executing
        progress: Optional progress percentage (0-100)
        message: Optional status message
    """
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    progress: Optional[int] = None
    message: Optional[str] = None

    @property
    def duration(self) -> Optional[float]:
        """Calculate task duration in seconds."""
        if self.start_time is None:
            return None
        end = self.end_time or time.time()
        return end - self.start_time

    @property
    def is_complete(self) -> bool:
        """Check if task has finished execution."""
        return self.status in {TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELLED}

    def start(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.RUNNING
        self.start_time = time.time()

    def complete(self, result: Any = None) -> None:
        """Mark task as successfully completed."""
        self.status = TaskStatus.SUCCESS
        self.result = result
        self.end_time = time.time()
        self.progress = 100

    def fail(self, error: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.error = error
        self.end_time = time.time()

    def cancel(self) -> None:
        """Mark task as cancelled."""
        self.status = TaskStatus.CANCELLED
        self.end_time = time.time()

    def update_progress(self, progress: int, message: Optional[str] = None) -> None:
        """Update task progress.

        Args:
            progress: Progress percentage (0-100)
            message: Optional status message
        """
        self.progress = max(0, min(100, progress))
        if message:
            self.message = message
