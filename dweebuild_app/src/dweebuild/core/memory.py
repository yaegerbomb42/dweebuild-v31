from collections import deque
from datetime import datetime
from typing import List, Dict, Any

class ProjectMemory:
    """
    Shared memory storage for the Dweebuild session.
    Stores logs, knowledge, and file caches shared between agents.
    """
    def __init__(self):
        self.logs: deque = deque(maxlen=1000)
        self.kv_store: Dict[str, Any] = {}
        self.project_context: Dict[str, str] = {} # e.g. path -> content summary
    
    def add_log(self, source: str, message: str, level: str = "INFO"):
        """Add a centralized log entry."""
        ts = datetime.now().strftime("%H:%M:%S")
        entry = {
            "timestamp": ts,
            "source": source,
            "level": level,
            "message": message
        }
        self.logs.append(entry)
        # In a real app, we might write to disk or db here
        
    def get_logs(self, limit: int = 50) -> List[Dict]:
        """Retrieve recent logs."""
        return list(self.logs)[-limit:]

    def update_context(self, key: str, value: Any):
        self.kv_store[key] = value

    def get_context(self, key: str) -> Any:
        return self.kv_store.get(key)
