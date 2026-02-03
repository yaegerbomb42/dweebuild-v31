from ..core.agent import BaseAgent
from ..core.llm import LLMClient
from ..tools.std_tools import FileWriteTool
import os

class ArchitectAgent(BaseAgent):
    """
    The Architect is responsible for defining the project structure and interfaces.
    """
    def __init__(self, mission: str, project_root: str):
        super().__init__("ARCHITECT", "System Designer", mission)
        self.llm = LLMClient()
        self.project_root = project_root
        # Auto-equip tools
        self.equip(FileWriteTool(project_root))

    async def _plan_next_step(self, task: str, context: str) -> dict:
        system_prompt = """
        You are the Chief Architect (The "Manus" of this system).
        Your goal is to scaffold the project structure.
        
        AVAILABLE TOOLS:
        - file_write(filepath, content): Create/Update files.
        - FINAL_ANSWER(result): When the architecture is strictly complete.
        
        STRATEGY:
        1. Think about the file structure needed for the MISSION.
        2. Create files one by one (or in batches if you want).
        3. E.g. `file_write("src/main.py", "...")`.
        4. When done, call FINAL_ANSWER("Architecture complete").
        
        Return JSON ONLY:
        {
            "thought": "I need to create the main entry point...",
            "tool": "file_write",
            "args": { "filepath": "...", "content": "..." }
        }
        """
        
        user_prompt = f"""
        MISSION: {self.mission}
        TASK: {task}
        CONTEXT: {context}
        """
        
        return await self.llm.get_json(system_prompt, user_prompt)

    def _gather_context(self) -> str:
        return f"Files created so far: {list(self.tools['file_write'].root_dir)}" # Pseudo-context
