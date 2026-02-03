import os
from pathlib import Path
from typing import Optional

class Config:
    """Centralized configuration management."""
    
    def __init__(self):
        self._load_env()
    
    def _load_env(self):
        """Load from .env file if it exists."""
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    
    @property
    def groq_api_key(self) -> Optional[str]:
        return os.getenv("GROQ_API_KEY")
    
    @property
    def openai_api_key(self) -> Optional[str]:
        return os.getenv("OPENAI_API_KEY")
    
    @property
    def anthropic_api_key(self) -> Optional[str]:
        return os.getenv("ANTHROPIC_API_KEY")
    
    @property
    def max_concurrent_agents(self) -> int:
        return int(os.getenv("MAX_CONCURRENT_AGENTS", "3"))
    
    @property
    def agent_timeout(self) -> int:
        return int(os.getenv("AGENT_TIMEOUT_SECONDS", "300"))
    
    @property
    def git_auto_commit(self) -> bool:
        return os.getenv("GIT_AUTO_COMMIT", "false").lower() == "true"
    
    @property
    def dashboard_port(self) -> int:
        return int(os.getenv("DASHBOARD_PORT", "8501"))
    
    @property
    def enable_animations(self) -> bool:
        return os.getenv("ENABLE_ANIMATIONS", "true").lower() == "true"
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration. Returns (is_valid, missing_keys)."""
        missing = []
        if not self.groq_api_key:
            missing.append("GROQ_API_KEY")
        return (len(missing) == 0, missing)

# Global config instance
config = Config()
