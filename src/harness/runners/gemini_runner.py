"""Task runner using gemini-cli for AI-powered task execution."""

import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional


class GeminiRunner:
    """Execute tasks using gemini-cli.

    This runner enables AI-powered task execution by invoking gemini-cli
    with task prompts, similar to how Ralph uses AI agents.
    """

    def __init__(
        self,
        gemini_cli_path: str = "gemini",
        model: Optional[str] = None,
        working_dir: Optional[Path] = None,
    ):
        """Initialize the Gemini runner.

        Args:
            gemini_cli_path: Path to gemini-cli executable (default: "gemini" in PATH)
            model: Optional Gemini model to use (e.g., "gemini-2.0-flash-exp")
            working_dir: Optional working directory for command execution
        """
        self.gemini_cli_path = gemini_cli_path
        self.model = model
        self.working_dir = working_dir or Path.cwd()

    def check_gemini_available(self) -> bool:
        """Check if gemini-cli is available.

        Returns:
            True if gemini-cli is installed and accessible
        """
        try:
            result = subprocess.run(
                [self.gemini_cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    async def run(self, task_data: dict) -> Any:
        """Execute a task using gemini-cli.

        Args:
            task_data: Task data dictionary containing at minimum a "prompt" field

        Returns:
            Result from gemini-cli execution

        Raises:
            ValueError: If task_data is missing required fields
            RuntimeError: If gemini-cli execution fails
        """
        # Extract prompt from task data
        prompt = task_data.get("prompt")
        if not prompt:
            raise ValueError("Task must have a 'prompt' field for Gemini execution")

        # Check if gemini-cli is available
        if not self.check_gemini_available():
            raise RuntimeError(
                f"gemini-cli not found at '{self.gemini_cli_path}'. "
                "Install it with: npm install -g @google/gemini-cli"
            )

        # Build command
        cmd = [self.gemini_cli_path]

        # Add model if specified
        if self.model:
            cmd.extend(["--model", self.model])

        # Add any additional gemini-cli flags from task_data
        if task_data.get("auto_approve"):
            cmd.append("--yes")

        if task_data.get("json_output"):
            cmd.append("--json")

        # Add the prompt
        cmd.append(prompt)

        # Execute gemini-cli
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"gemini-cli failed: {error_msg}")

            output = stdout.decode()

            # Parse JSON output if requested
            if task_data.get("json_output"):
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    return {"raw_output": output}

            return output

        except asyncio.TimeoutError:
            raise RuntimeError("gemini-cli execution timed out")
        except Exception as e:
            raise RuntimeError(f"Error executing gemini-cli: {str(e)}")

    def __call__(self, task_data: dict) -> Any:
        """Synchronous wrapper for run method.

        Args:
            task_data: Task data dictionary

        Returns:
            Result from gemini-cli execution
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.run(task_data))


def create_gemini_runner(
    model: Optional[str] = None,
    working_dir: Optional[Path] = None,
) -> GeminiRunner:
    """Factory function to create a Gemini runner.

    Args:
        model: Optional Gemini model to use
        working_dir: Optional working directory

    Returns:
        Configured GeminiRunner instance
    """
    return GeminiRunner(model=model, working_dir=working_dir)
