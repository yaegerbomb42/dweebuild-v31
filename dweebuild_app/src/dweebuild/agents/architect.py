import asyncio
from typing import Dict, Any

from ..core.agent import BaseAgent
from ..core.tech_advisor import TechStackAdvisor
from ..tools.std_tools import FileWriteTool

class ArchitectAgent(BaseAgent):
    """
    The Chief Architect: Designs the system structure before implementation.
    Now with intelligent tech stack selection.
    """
    def __init__(self, mission: str, working_dir: str):
        super().__init__(name="ARCHITECT", role="System Designer", mission=mission)
        self.working_dir = working_dir
        self.equip(FileWriteTool(working_dir))
        self.tech_advisor = TechStackAdvisor()
        
        # Get tech recommendations
        self.tech_recommendation = self.tech_advisor.get_recommendation_prompt(mission)

    async def _plan_next_step(self, task: str, context: str) -> Dict[str, Any]:
        """
        Enhanced Architect planning with tech stack intelligence.
        """
        system_prompt = """
        You are the Chief Architect (The "Manus" of this system).
        Your goal is to scaffold a PRODUCTION-QUALITY project structure.
        
        CRITICAL: Choose technology based on project scope!
        - Simple CLI? Use Click/Typer
        - 2D Game? Use Pygame/Arcade
        - 3D Game with detailed rendering? Use Panda3D/Ursina/Godot
        - Web App? Use FastAPI/Django
        
        DO NOT use weak tools for big projects (e.g., Pygame for 3D is WRONG).
        
        AVAILABLE TOOLS:
        - file_write(filepath, content): Create/Update files.
        - FINAL_ANSWER(result): When the architecture is strictly complete.
        
        STRATEGY:
        1. Review tech recommendations below
        2. Think about what files are needed for a PROFESSIONAL project
        3. Create comprehensive structure (src/, tests/, docs/, requirements.txt, README)
        4. Include proper dependencies for chosen tech stack
        5. E.g. `file_write("requirements.txt", "panda3d>=1.10\\npymunk>=6.0")`.
        6. Create skeleton files with TODO comments for the Engineer
        7. When done, call FINAL_ANSWER("Architecture complete with [tech stack]").
        
        Return JSON ONLY:
        {
            "thought": "Based on the recommendations, I should use Panda3D for this 3D game...",
            "tool": "file_write",
            "args": { "filepath": "...", "content": "..." }
        }
        """
        
        user_prompt = f"""
        MISSION: {self.mission}
        CURRENT TASK: {task}
        CONTEXT: {context}
        
        {self.tech_recommendation}
        
        Design a professional project structure. Choose the RIGHT technology for the scope.
        """
        
        result = await self.llm.chat(system_prompt, user_prompt)
        
        try:
            import json
            return json.loads(result)
        except:
            return {"thought": result, "tool": "FINAL_ANSWER", "args": {"result": result}}
