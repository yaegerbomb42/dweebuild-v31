from enum import Enum
from typing import Optional
from dataclasses import dataclass

class WorkMode(Enum):
    """Operation modes for the Dweebuild system."""
    SINGLE = "single"           # Run once, await user approval
    AUTONOMOUS = "autonomous"    # Continuous improvement until stopped
    SUPERVISED = "supervised"    # Prompt user at key decision points

@dataclass
class ModeConfig:
    """Configuration for operation mode."""
    mode: WorkMode
    max_iterations: Optional[int] = None  # None = unlimited for AUTONOMOUS
    require_approval_for: list[str] = None  # e.g., ["file_write", "shell_exec"]
    auto_commit: bool = False
    
    def __post_init__(self):
        if self.require_approval_for is None:
            if self.mode == WorkMode.SINGLE:
                self.require_approval_for = ["all"]
            elif self.mode == WorkMode.SUPERVISED:
                self.require_approval_for = ["file_write", "git"]
            else:  # AUTONOMOUS
                self.require_approval_for = []

    def requires_approval(self, tool_name: str) -> bool:
        """Check if a tool requires user approval in this mode."""
        if "all" in self.require_approval_for:
            return True
        return tool_name in self.require_approval_for
