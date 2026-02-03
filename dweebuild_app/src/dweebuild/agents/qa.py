from ..core.agent import BaseAgent
from ..tools.std_tools import PytestTool

class QAAgent(BaseAgent):
    """
    The QA Lead runs tests and rejects work if they fail.
    """
    def __init__(self, mission: str, project_root: str):
        super().__init__("QA_LEAD", "Quality Assurance", mission)
        self.equip(PytestTool(project_root))

    async def run(self, task: str) -> str:
        self.status = "WORKING"
        self.log(f"QA initiated for: {task}")
        
        # 1. Run Tests
        self.thought = "Running full test suite..."
        self.log(self.thought, "CMD")
        
        tester = self.tools["run_tests"]
        output = await tester.execute()
        
        # 2. Analyze Results
        if "failed" in output.lower() or "error" in output.lower():
            self.status = "REJECTED"
            self.log("Tests FAILED.", "ERR")
            self.log(output[-200:]) # Log last few lines
            return f"QA FAILURE. Revert or Fix. Output: {output[-100:]}"
        else:
            self.status = "IDLE"
            self.log("Tests PASSED.", "SUCCESS")
            return "QA SUCCESS. Deployment Approved."
