"""Task runner for executing shell commands."""

import asyncio
import subprocess
from pathlib import Path
from typing import Any, Optional


class ShellRunner:
    """Execute tasks as shell commands.

    This runner executes tasks by running shell commands specified in the task data.
    """

    def __init__(self, working_dir: Optional[Path] = None, shell: str = "/bin/bash"):
        """Initialize the Shell runner.

        Args:
            working_dir: Optional working directory for command execution
            shell: Shell to use for execution (default: /bin/bash)
        """
        self.working_dir = working_dir or Path.cwd()
        self.shell = shell

    async def run(self, task_data: dict) -> Any:
        """Execute a task as a shell command.

        Args:
            task_data: Task data dictionary containing a "command" field

        Returns:
            Command output

        Raises:
            ValueError: If task_data is missing required fields
            RuntimeError: If command execution fails
        """
        command = task_data.get("command")
        if not command:
            raise ValueError("Task must have a 'command' field for shell execution")

        timeout = task_data.get("timeout", 300)  # Default 5 minutes

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir,
                shell=True,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise RuntimeError(f"Command timed out after {timeout} seconds")

            output = stdout.decode()
            error = stderr.decode()

            if process.returncode != 0:
                raise RuntimeError(
                    f"Command failed with exit code {process.returncode}\n"
                    f"Output: {output}\n"
                    f"Error: {error}"
                )

            return output if output else error

        except Exception as e:
            if isinstance(e, RuntimeError):
                raise
            raise RuntimeError(f"Error executing command: {str(e)}")

    def __call__(self, task_data: dict) -> Any:
        """Synchronous wrapper for run method.

        Args:
            task_data: Task data dictionary

        Returns:
            Command output
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.run(task_data))
