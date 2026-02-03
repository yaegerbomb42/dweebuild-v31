import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from dweebuild.core.memory import ProjectMemory
from dweebuild.core.modes import WorkMode


class SessionManager:
    """
    Handles saving and restoring session state.
    """
    def __init__(self, sessions_dir: str = "sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session_id: str, state: Dict[str, Any]) -> str:
        """
        Save the current session state to disk.
        
        Args:
            session_id: Unique session identifier
            state: Dict containing orchestrator state, agent states, memory, etc.
        
        Returns:
            Path to saved session file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{session_id}_{timestamp}.json"
        filepath = self.sessions_dir / filename
        
        # Serialize state
        serialized = {
            "session_id": session_id,
            "timestamp": timestamp,
            "mode": state.get("mode", "SINGLE"),
            "agents": {},
            "tasks": state.get("tasks", []),
            "logs": state.get("logs", []),
            "iteration_count": state.get("iteration_count", 0)
        }
        
        # Serialize agent states
        for name, agent in state.get("agents", {}).items():
            serialized["agents"][name] = {
                "status": agent.status,
                "thought": agent.thought,
                "logs": list(agent.logs)
            }
        
        with open(filepath, 'w') as f:
            json.dump(serialized, f, indent=2)
        
        return str(filepath)

    def load_session(self, filepath: str) -> Dict[str, Any]:
        """
        Restore a session from disk.
        
        Returns:
            Dict containing the restored state
        """
        with open(filepath, 'r') as f:
            return json.load(f)

    def list_sessions(self) -> list[str]:
        """List all available saved sessions."""
        return [str(p) for p in self.sessions_dir.glob("*.json")]

    def export_logs(self, session_id: str, logs: list) -> str:
        """Export logs to a markdown file."""
        filename = f"{session_id}_logs.md"
        filepath = self.sessions_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"# Session Logs: {session_id}\n\n")
            for entry in logs:
                ts = entry.get('timestamp', 'N/A')
                source = entry.get('source', 'UNKNOWN')
                level = entry.get('level', 'INFO')
                msg = entry.get('message', '')
                f.write(f"**[{ts}] [{source}] [{level}]** {msg}\n\n")
        
        return str(filepath)
