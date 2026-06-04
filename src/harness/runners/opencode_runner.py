"""Task runner using OpenCode for AI-powered task execution."""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any, Optional


class OpenCodeRunner:
    """Execute tasks using OpenCode AI coding agent.

    OpenCode is an open-source, terminal-first AI coding agent that supports
    75+ LLM providers including OpenAI, Anthropic, Google Gemini, and local
    models via Ollama.
    """

    def __init__(
        self,
        opencode_cli_path: str = "opencode",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        mode: str = "build",
        working_dir: Optional[Path] = None,
    ):
        """Initialize the OpenCode runner.

        Args:
            opencode_cli_path: Path to opencode executable (default: "opencode" in PATH)
            provider: Optional provider (e.g., "anthropic", "openai", "google")
            model: Optional model name (e.g., "claude-sonnet-4-5", "gpt-4")
            mode: Agent mode - "build" (default) or "plan"
            working_dir: Optional working directory for command execution
        """
        self.opencode_cli_path = opencode_cli_path
        self.provider = provider
        self.model = model
        self.mode = mode
        self.working_dir = working_dir or Path.cwd()

    def check_opencode_available(self) -> bool:
        """Check if OpenCode is available.

        Returns:
            True if OpenCode is installed and accessible
        """
        try:
            result = subprocess.run(
                [self.opencode_cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    async def run(self, task_data: dict) -> Any:
        """Execute a task using OpenCode.

        Args:
            task_data: Task data dictionary containing at minimum a "prompt" field

        Returns:
            Result from OpenCode execution

        Raises:
            ValueError: If task_data is missing required fields
            RuntimeError: If OpenCode execution fails
        """
        # Extract prompt from task data
        prompt = task_data.get("prompt")
        if not prompt:
            raise ValueError("Task must have a 'prompt' field for OpenCode execution")

        # Check if OpenCode is available
        if not self.check_opencode_available():
            raise RuntimeError(
                f"OpenCode not found at '{self.opencode_cli_path}'. "
                "Install it with: curl -fsSL https://opencode.ai/install | sh"
            )

        # Build command
        cmd = [self.opencode_cli_path]

        # Add provider if specified (override instance default if provided in task)
        provider = task_data.get("provider", self.provider)
        if provider:
            cmd.extend(["--provider", provider])

        # Add model if specified
        model = task_data.get("model", self.model)
        if model:
            cmd.extend(["--model", model])

        # Add mode (build or plan)
        mode = task_data.get("mode", self.mode)
        if mode in ["build", "plan"]:
            cmd.extend(["--mode", mode])

        # Add auto-approve flag if requested
        if task_data.get("auto_approve", False):
            cmd.append("--yes")

        # Add verbose flag if requested
        if task_data.get("verbose", False):
            cmd.append("--verbose")

        # Add JSON output flag if requested
        if task_data.get("json_output", False):
            cmd.append("--json")

        # Add the prompt
        cmd.append(prompt)

        # Execute OpenCode
        try:
            timeout = task_data.get("timeout", 600)  # Default 10 minutes

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise RuntimeError(f"OpenCode execution timed out after {timeout} seconds")

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"OpenCode failed: {error_msg}")

            output = stdout.decode()

            # Parse JSON output if requested
            if task_data.get("json_output"):
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    return {"raw_output": output}

            return output

        except asyncio.TimeoutError:
            raise RuntimeError("OpenCode execution timed out")
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise
            raise RuntimeError(f"Error executing OpenCode: {str(e)}")

    def __call__(self, task_data: dict) -> Any:
        """Synchronous wrapper for run method.

        Args:
            task_data: Task data dictionary

        Returns:
            Result from OpenCode execution
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.run(task_data))


def create_opencode_runner(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    mode: str = "build",
    working_dir: Optional[Path] = None,
) -> OpenCodeRunner:
    """Factory function to create an OpenCode runner.

    Args:
        provider: Optional LLM provider (anthropic, openai, google, etc.)
        model: Optional model name
        mode: Agent mode - "build" or "plan"
        working_dir: Optional working directory

    Returns:
        Configured OpenCodeRunner instance
    """
    return OpenCodeRunner(
        provider=provider,
        model=model,
        mode=mode,
        working_dir=working_dir,
    )
