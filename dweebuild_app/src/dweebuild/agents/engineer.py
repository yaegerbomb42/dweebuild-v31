from ..core.agent import BaseAgent
from ..core.llm import LLMClient
from ..tools.std_tools import FileWriteTool, ShellTool
import os

class EngineerAgent(BaseAgent):
    """
    The Engineer writes code and corresponding tests.
    """
    def __init__(self, mission: str, project_root: str):
        super().__init__("ENGINEER", "Python Developer", mission)
        self.llm = LLMClient()
        self.project_root = project_root
        self.equip(FileWriteTool(project_root))
        self.equip(ShellTool())

    async def _plan_next_step(self, task: str, context: str) -> dict:
        """
        Engineer's brain: Analyzes the codebase and decides whether to read, write, or finish.
        """
        system_prompt = """
        You are a Principal Software Engineer (Manus/Claude Level).
        Your goal is to implement features with precision.
        
        AVAILABLE TOOLS:
        - shell_exec(cmd): Run terminal commands (find, grep, ls).
        - file_write(filepath, content): Write code to files.
        - FINAL_ANSWER(result): When the task is fully complete.

        STRATEGY:
        1. IF you don't know the file structure -> `shell_exec("find . ...")`
        2. IF you need to see existing code -> `shell_exec("cat ...")`
        3. IF you are ready to implement -> `file_write(...)`
        4. IF you have written both Source and Test -> `FINAL_ANSWER`
        
        Return JSON ONLY:
        {
            "thought": "Reasoning about what to do next...",
            "tool": "tool_name",
            "args": { ... }
        }
        """
        
        user_prompt = f"""
        MISSION: {self.mission}
        CURRENT TASK: {task}
        CONTEXT: {context}
        """
        
        return await self.llm.get_json(system_prompt, user_prompt)

    def _gather_context(self) -> str:
        # Pull recent logs or specific memory keys
        # In a real app this uses the 'memory' object deeply
        return "Last relevant log: " + str(list(self.logs)[-1] if self.logs else "None")
