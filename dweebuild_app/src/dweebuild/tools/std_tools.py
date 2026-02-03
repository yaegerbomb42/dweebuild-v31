import asyncio
import os
import subprocess
from typing import Any, Optional
from pathlib import Path
from .tool import BaseTool

# === EXISTING TOOLS (Enhanced) ===

class ShellTool(BaseTool):
    """Executes shell commands."""
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
    """Writes content to a file."""
    def __init__(self, root_dir: str):
        super().__init__("file_write", "Writes content to a file.")
        self.root_dir = root_dir

    async def execute(self, filepath: str, content: str, **kwargs) -> str:
        full_path = os.path.abspath(os.path.join(self.root_dir, filepath))
        if not full_path.startswith(os.path.abspath(self.root_dir)):
            return "ERROR: Access denied (Path traversal attempt)."
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"

class PytestTool(BaseTool):
    """Runs pytest on a specific directory or file."""
    def __init__(self, root_dir: str):
        super().__init__("run_tests", "Runs pytest and returns results.")
        self.shell = ShellTool()
        self.root_dir = root_dir

    async def execute(self, target: str = "tests", **kwargs) -> str:
        cmd = f"pytest {target}"
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

# === NEW TOOLS ===

class FileReadTool(BaseTool):
    """Safely reads file contents."""
    def __init__(self, root_dir: str):
        super().__init__("file_read", "Reads the contents of a file.")
        self.root_dir = root_dir

    async def execute(self, filepath: str, **kwargs) -> str:
        full_path = os.path.abspath(os.path.join(self.root_dir, filepath))
        if not full_path.startswith(os.path.abspath(self.root_dir)):
            return "ERROR: Access denied"
        
        if not os.path.exists(full_path):
            return f"ERROR: File not found: {filepath}"
        
        try:
            with open(full_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"ERROR: {str(e)}"

class GrepTool(BaseTool):
    """Searches for patterns in the codebase."""
    def __init__(self, root_dir: str):
        super().__init__("grep", "Searches for text patterns in files.")
        self.root_dir = root_dir

    async def execute(self, pattern: str, path: str = ".", **kwargs) -> str:
        cmd = f"grep -r '{pattern}' {path}"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.root_dir
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode() if stdout else "No matches found."

class GitTool(BaseTool):
    """Git operations."""
    def __init__(self, root_dir: str):
        super().__init__("git", "Performs git operations (status, commit, push).")
        self.root_dir = root_dir

    async def execute(self, action: str, message: str = "", **kwargs) -> str:
        commands = {
            "status": "git status",
            "add_all": "git add .",
            "commit": f"git commit -m '{message}'",
            "push": "git push",
            "diff": "git diff",
        }
        
        if action not in commands:
            return f"ERROR: Unknown git action: {action}"
        
        cmd = commands[action]
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.root_dir
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode() + stderr.decode()

class PipTool(BaseTool):
    """Install Python packages."""
    def __init__(self):
        super().__init__("pip_install", "Installs Python packages via pip.")

    async def execute(self, package: str, **kwargs) -> str:
        cmd = f"pip install -q {package}"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            return f"Successfully installed {package}"
        return f"ERROR installing {package}: {stderr.decode()}"

class WebSearchTool(BaseTool):
    """Performs web searches."""
    def __init__(self):
        super().__init__("web_search", "Searches the web using DuckDuckGo.")

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> str:
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append(f"**{r['title']}**\n{r['href']}\n{r['body']}\n")
            return "\n---\n".join(results) if results else "No results found."
        except Exception as e:
            return f"ERROR: {str(e)}"

class DirectoryTool(BaseTool):
    """Lists directory contents."""
    def __init__(self, root_dir: str):
        super().__init__("list_dir", "Lists files and directories.")
        self.root_dir = root_dir

    async def execute(self, path: str = ".", **kwargs) -> str:
        full_path = os.path.join(self.root_dir, path)
        if not os.path.exists(full_path):
            return f"ERROR: Path not found: {path}"
        
        try:
            items = os.listdir(full_path)
            return "\n".join(items)
        except Exception as e:
            return f"ERROR: {str(e)}"

class LintTool(BaseTool):
    """Runs code linting."""
    def __init__(self, root_dir: str):
        super().__init__("lint", "Runs pylint or ruff on code.")
        self.root_dir = root_dir

    async def execute(self, target: str = ".", **kwargs) -> str:
        # Try ruff first, fallback to pylint
        for cmd in [f"ruff check {target}", f"pylint {target}"]:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.root_dir
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 127:  # Command exists
                return stdout.decode() + stderr.decode()
        return "No linter found. Install ruff or pylint."

class FormatTool(BaseTool):
    """Formats code with black."""
    def __init__(self, root_dir: str):
        super().__init__("format_code", "Formats Python code with black.")
        self.root_dir = root_dir

    async def execute(self, target: str = ".", **kwargs) -> str:
        cmd = f"black {target}"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.root_dir
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode() if proc.returncode == 0 else f"ERROR: {stderr.decode()}"

class ComplexityTool(BaseTool):
    """Analyzes code complexity."""
    def __init__(self, root_dir: str):
        super().__init__("complexity", "Analyzes cyclomatic complexity with radon.")
        self.root_dir = root_dir

    async def execute(self, target: str = ".", **kwargs) -> str:
        cmd = f"radon cc {target} -a"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.root_dir
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode() if proc.returncode == 0 else "Radon not installed."

class CoverageTool(BaseTool):
    """Runs test coverage."""
    def __init__(self, root_dir: str):
        super().__init__("coverage", "Runs pytest with coverage.")
        self.root_dir = root_dir

    async def execute(self, **kwargs) -> str:
        cmd = "pytest --cov=. --cov-report=term"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.root_dir
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode() + stderr.decode()
