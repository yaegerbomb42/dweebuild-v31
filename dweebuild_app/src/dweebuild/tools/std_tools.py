import asyncio
import os
import subprocess
from typing import Any
from .tool import BaseTool

class ShellTool(BaseTool):
    """
    Executes shell commands.
    """
    def __init__(self):
        super().__init__("shell_exec", "Executes a shell command and returns output.")

    async def execute(self, cmd: str, **kwargs) -> str:
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                return f"ERROR (Exit {proc.returncode}): {stderr.decode().strip()}"
            return stdout.decode().strip()
        except Exception as e:
            return f"EXECUTION ERROR: {str(e)}"

class FileWriteTool(BaseTool):
    """
    Writes content to a file.
    """
    def __init__(self, root_dir: str):
        super().__init__("file_write", "Writes content to a file.")
        self.root_dir = root_dir

    async def execute(self, filepath: str, content: str, **kwargs) -> str:
        # Security check: prevent escaping root
        full_path = os.path.abspath(os.path.join(self.root_dir, filepath))
        if not full_path.startswith(os.path.abspath(self.root_dir)):
            return "ERROR: Access denied (Path traversal attempt)."
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"

class PytestTool(BaseTool):
    """
    Runs pytest on a specific directory or file.
    """
    def __init__(self, root_dir: str):
        super().__init__("run_tests", "Runs pytest and returns results.")
        self.shell = ShellTool()
        self.root_dir = root_dir

    async def execute(self, target: str = "tests", **kwargs) -> str:
        cmd = f"pytest {target}"
        # We run this inside the root dir
        # For simplicity, we just use the ShellTool logic but we might need cwd
        # Let's manual impl to force cwd
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.root_dir
            )
            stdout, stderr = await proc.communicate()
            output = stdout.decode() + "\n" + stderr.decode()
            return output
        except Exception as e:
            return str(e)
