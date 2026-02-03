import asyncio
from typing import Dict, Any

from ..core.agent import BaseAgent
from ..tools.std_tools import FileWriteTool, ShellTool

class EngineerAgent(BaseAgent):
    """
    The Principal Software Engineer: Implements features with precision.
    Enhanced with complexity recognition and appropriate coding standards.
    """
    def __init__(self, mission: str, working_dir: str):
        super().__init__(name="ENGINEER", mission=mission)
        self.working_dir = working_dir
        self.equip(ShellTool())
        self.equip(FileWriteTool(working_dir))
        
        # Detect project complexity
        self.is_complex_project = self._assess_complexity(mission)

    def _assess_complexity(self, mission: str) -> bool:
        """Determine if this is a complex project requiring high standards."""
        complex_keywords = [
            "3d", "gta", "detailed", "rendering", "physics engine",
            "distributed", "microservices", "enterprise", "scalable"
        ]
        return any(kw in mission.lower() for kw in complex_keywords)

    async def _plan_next_step(self, task: str, context: str) -> Dict[str, Any]:
        """
        Enhanced planning with complexity-aware code generation.
        """
        
        # Adjust standards based on complexity
        quality_standard = "PRODUCTION-GRADE" if self.is_complex_project else "PROFESSIONAL"
        code_depth = "comprehensive, well-architected" if self.is_complex_project else "clean, functional"
        
        system_prompt = f"""
        You are a {quality_standard} Principal Software Engineer.
        Your goal is to implement features with {code_depth} code.
        
        PROJECT COMPLEXITY: {"HIGH - Use best practices, design patterns, proper separation of concerns" if self.is_complex_project else "MODERATE - Write clean, maintainable code"}
        
        AVAILABLE TOOLS:
        - shell_exec(cmd): Run terminal commands (find, grep, ls, cat).
        - file_write(filepath, content): Write code to files.
        - FINAL_ANSWER(result): When the task is fully complete.

        STRATEGY:
        1. IF you don't know the file structure -> `shell_exec("find . -name '*.py'")`
        2. IF you need to see existing code -> `shell_exec("cat filepath")`
        3. IF you need to check dependencies -> `shell_exec("cat requirements.txt")`
        4. IF you are ready to implement -> `file_write(...)`
        5. Write BOTH source code AND comprehensive tests
        6. IF you have written both Source and Test -> `FINAL_ANSWER`
        
        CODE QUALITY REQUIREMENTS:
        {"- Use design patterns (Factory, Observer, etc.)" if self.is_complex_project else ""}
        {"- Implement proper error handling" if self.is_complex_project else ""}
        {"- Add detailed docstrings" if self.is_complex_project else ""}
        - Follow PEP 8
        - Include type hints
        - Write comprehensive tests
        
        Return JSON ONLY:
        {{
            "thought": "Reasoning about what to do next...",
            "tool": "tool_name",
            "args": {{ ... }}
        }}
        """
        
        user_prompt = f"""
        MISSION: {self.mission}
        CURRENT TASK: {task}
        CONTEXT: {context}
        """
        
        result = await self.llm.chat(system_prompt, user_prompt)
        
        try:
            import json
            return json.loads(result)
        except:
            return {"thought": result, "tool": "FINAL_ANSWER", "args": {"result": result}}
