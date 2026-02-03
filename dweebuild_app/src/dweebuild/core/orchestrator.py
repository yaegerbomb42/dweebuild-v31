import asyncio
from collections import deque
from typing import Dict, List, Optional

from .agent import BaseAgent
from .memory import ProjectMemory

class Orchestrator:
    """
    The central hub that manages agents, task queues, and global state.
    """
    def __init__(self):
        self.memory = ProjectMemory()
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: deque = deque()
        self.is_running = False
    
    def register_agent(self, agent: BaseAgent):
        """Add an agent to the swarm."""
        agent.memory = self.memory # link memory
        self.agents[agent.name] = agent
        self.memory.add_log("SYSTEM", f"Agent {agent.name} registered.", "INFO")

    def add_task(self, task: str, priority: int = 0):
        """Add a task to the global queue."""
        if priority > 0:
            self.task_queue.appendleft(task)
        else:
            self.task_queue.append(task)
        self.memory.add_log("SYSTEM", f"Task queued: {task}", "INFO")

    async def run_step(self):
        """
        Execute one step of the swarm logic.
        This is designed to be called in a loop (e.g. from Streamlit or an async loop).
        """
        if not self.is_running:
            return

        # 1. Check for idle agents
        # 2. Check for pending tasks
        # 3. Assign tasks to appropriate agents (Very simple routing for now)
        
        # Simple Logic: 
        # - If Architect is IDLE and no structure exists -> Architect work
        # - If Engineer is IDLE and task exists -> Engineer work
        # - If QA is IDLE and verify task exists -> QA work
        
        # NOTE: In a real system, this dispatch logic would be much more complex 
        # and likely driven by the agents self-selecting or a Supervisor LLM.
        
        # For v31 MVP, we will rely on the Agents' internal run loops to pick up work 
        # if given a task, or we explicitly hand-off here.
        
        pass

    def start(self):
        self.is_running = True
        self.memory.add_log("SYSTEM", "Orchestrator started.", "SUCCESS")

    def stop(self):
        self.is_running = False
        self.memory.add_log("SYSTEM", "Orchestrator stopped.", "WARN")
