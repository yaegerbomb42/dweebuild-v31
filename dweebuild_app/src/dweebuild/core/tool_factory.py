import os
import json
from pathlib import Path
from typing import Dict, Any
from .tool import BaseTool, FunctionalTool

class ToolFactory:
    """
    Allows agents to create their own tools at runtime.
    """
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.custom_tools: Dict[str, BaseTool] = {}
        self._load_existing_tools()

    def _load_existing_tools(self):
        """Load previously created custom tools."""
        manifest_path = self.storage_dir / "tool_manifest.json"
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                # TODO: Dynamically load tool implementations
                # For now, we just track their definitions

    async def create_tool(self, name: str, description: str, code: str) -> BaseTool:
        """
        Create a new tool from LLM-generated code.
        
        Args:
            name: Tool name
            description: What the tool does
            code: Python function code (as string)
        
        Returns:
            The created BaseTool instance
        """
        # Security: In production, this would use a sandbox
        # For MVP, we'll store the code and create a simple wrapper
        
        tool_file = self.storage_dir / f"{name}.py"
        with open(tool_file, 'w') as f:
            f.write(code)
        
        # Create manifest entry
        manifest_path = self.storage_dir / "tool_manifest.json"
        manifest = {}
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        
        manifest[name] = {
            "description": description,
            "file": str(tool_file),
            "created_at": str(Path(tool_file).stat().st_mtime)
        }
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # For now, return a placeholder
        # In production, we'd exec() the code in a sandboxed environment
        async def placeholder_func(**kwargs):
            return f"Custom tool '{name}' execution (sandboxing required for production)"
        
        tool = FunctionalTool(name, description, placeholder_func)
        self.custom_tools[name] = tool
        return tool

    def get_tool(self, name: str) -> BaseTool:
        """Retrieve a custom tool by name."""
        return self.custom_tools.get(name)

    def list_tools(self) -> list[str]:
        """List all available custom tools."""
        return list(self.custom_tools.keys())
