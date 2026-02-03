import asyncio
from collections import deque
from typing import Dict, List, Optional
import time

from .agent import BaseAgent
from .memory import ProjectMemory
from .modes import WorkMode, ModeConfig

class Orchestrator:
    """
    The central hub that manages agents, task queues, and global state.
    Now with true async concurrency and operation modes.
    """
    def __init__(self, mode: WorkMode = WorkMode.SINGLE):
        self.memory = ProjectMemory()
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: deque = deque()
        self.is_running = False
        self.mode_config = ModeConfig(mode=mode)
        self.iteration_count = 0
        self.agent_locks: Dict[str, asyncio.Lock] = {}
    
    def register_agent(self, agent: BaseAgent):
        """Add an agent to the swarm."""
        agent.memory = self.memory
        self.agents[agent.name] = agent
        self.agent_locks[agent.name] = asyncio.Lock()
        self.memory.add_log("SYSTEM", f"Agent {agent.name} registered.", "INFO")

    def add_task(self, task: str, priority: int = 0):
        """Add a task to the global queue."""
        if priority > 0:
            self.task_queue.appendleft(task)
        else:
            self.task_queue.append(task)
        self.memory.add_log("SYSTEM", f"Task queued: {task}", "INFO")

    async def run_concurrent(self):
        """
        Execute agents concurrently using asyncio.gather().
        This is the main concurrent execution loop.
        """
        if not self.is_running:
            return
        
        # Gather all agent tasks
        agent_tasks = []
        for agent in self.agents.values():
            if agent.status == "IDLE" and self.task_queue:
                # Check if agent can process the next task
                task = self._route_task_to_agent(agent)
                if task:
                    agent_tasks.append(self._run_agent_safe(agent, task))
        
        if agent_tasks:
            # Run all agents concurrently
            results = await asyncio.gather(*agent_tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    self.memory.add_log("SYSTEM", f"Agent error: {result}", "ERR")
    
    def _route_task_to_agent(self, agent: BaseAgent) -> Optional[str]:
        """Route appropriate task to agent based on their role."""
        if not self.task_queue:
            return None
        
        # Simple routing logic
        task = self.task_queue[0]
        task_lower = task.lower()
        
        if "design" in task_lower or "architecture" in task_lower:
            if agent.name == "ARCHITECT":
                return self.task_queue.popleft()
        elif "implement" in task_lower or "fix" in task_lower or "create" in task_lower:
            if agent.name == "ENGINEER":
                return self.task_queue.popleft()
        elif "test" in task_lower or "verify" in task_lower or "qa" in task_lower:
            if agent.name == "QA_LEAD":
                return self.task_queue.popleft()
        
        return None
    
    async def _run_agent_safe(self, agent: BaseAgent, task: str):
        """Run agent with timeout and error handling."""
        async with self.agent_locks[agent.name]:
            try:
                result = await asyncio.wait_for(
                    agent.run(task),
                    timeout=300  # 5 minute timeout
                )
                self.memory.add_log(agent.name, f"Completed: {task[:50]}...", "SUCCESS")
                return result
            except asyncio.TimeoutError:
                self.memory.add_log(agent.name, "Task timeout", "ERR")
                agent.status = "ERROR"
            except Exception as e:
                self.memory.add_log(agent.name, f"Error: {e}", "ERR")
                agent.status = "ERROR"

    def start(self):
        self.is_running = True
        self.iteration_count = 0
        self.memory.add_log("SYSTEM", f"Orchestrator started in {self.mode_config.mode.value.upper()} mode.", "SUCCESS")

    def stop(self):
        self.is_running = False
        self.memory.add_log("SYSTEM", "Orchestrator stopped.", "WARN")
    
    def should_continue(self) -> bool:
        """Check if the orchestrator should continue based on mode."""
        if not self.is_running:
            return False
        
        if self.mode_config.mode == WorkMode.SINGLE:
            # Run until queue is empty
            return len(self.task_queue) > 0
        
        if self.mode_config.mode == WorkMode.AUTONOMOUS:
            # Run indefinitely (or until max_iterations)
            if self.mode_config.max_iterations:
                return self.iteration_count < self.mode_config.max_iterations
            return True
        
        if self.mode_config.mode == WorkMode.SUPERVISED:
            # User-controlled
            return True
        
        return True

