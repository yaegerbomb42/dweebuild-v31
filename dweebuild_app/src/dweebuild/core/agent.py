import asyncio
from typing import List, Dict, Any, Optional
from collections import deque
from datetime import datetime
import abc

class AgentAttribute:
    """Helper to store agent state attributes."""
    def __init__(self, value=None):
        self.value = value

class BaseAgent(abc.ABC):
    """
    Abstract Base Class for Dweebuild Agents.
    """
    def __init__(self, name: str, role: str, mission: str):
        from .llm import LLMClient
        self.name = name
        self.role = role
        self.mission = mission
        self.status = "IDLE"
        self.thought = "Standby"
        self.logs = deque(maxlen=100)
        self.tools = {}
        self.memory = None # Assigned by Orchestrator
        self.llm = LLMClient()  # Every agent gets an LLM client

    def equip(self, tool):
        """Register a tool for the agent to use."""
        self.tools[tool.name] = tool
        self.log(f"Equipped tool: {tool.name}", "INFO")

    def log(self, message: str, level: str = "INFO"):
        """Log a message to the agent's internal log and shared memory."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(entry)
        # TODO: Push to shared memory if available
        
    async def run(self, task: str) -> str:
        """
        Executes the agent's main loop using a ReAct (Reasoning + Acting) pattern.
        """
        self.status = "WORKING"
        self.mission_context = task
        self.log(f"Starting ReAct Loop for: {task}", "INFO")

        attempts = 0
        max_attempts = 5

        while attempts < max_attempts:
            attempts += 1
            
            # 1. PERCEPTION: Gather Context
            context = self._gather_context()
            
            # 2. REASONING: Decide next step
            plan = await self._plan_next_step(task, context)
            self.thought = plan.get("thought", "Thinking...")
            self.log(f"Thought: {self.thought}", "INFO")
            
            tool_name = plan.get("tool")
            tool_args = plan.get("args", {})
            
            # 3. ACTION
            if tool_name == "FINAL_ANSWER":
                self.status = "IDLE"
                return plan.get("result", "Task Completed")
            
            if tool_name in self.tools:
                try:
                    self.log(f"Action: {tool_name} {tool_args}", "CMD")
                    result = await self.tools[tool_name].execute(**tool_args)
                    self.log(f"Observation: {str(result)[:100]}...", "SUCCESS")
                    # Store observation for next turn
                    self.memory.add_log(self.name, f"Tool Output: {result}", "DEBUG")
                except Exception as e:
                    self.log(f"Action Failed: {e}", "ERR")
            else:
                self.log(f"Unknown Tool: {tool_name}", "WARN")
                
        self.status = "ERROR"
        return "Max attempts reached without resolution."

    async def _plan_next_step(self, task: str, context: str) -> Dict[str, Any]:
        """
        Uses LLM to decide the next action based on history.
        """
        # This is a simplified version. In a real generalized agent, 
        # we would pass the full conversation history.
        # For Dweebuild v31 specific agents, we override this or use a specific prompt.
        return {"tool": "FINAL_ANSWER", "result": "Default BaseAgent has no brain."}

    def _gather_context(self) -> str:
        """Collects relevant state from memory."""
        return "Context gathering not implemented in Base."
