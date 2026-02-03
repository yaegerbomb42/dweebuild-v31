import abc
from typing import Any, Callable

class BaseTool(abc.ABC):
    """
    Abstract Base Class for Tools.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abc.abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool's functionality.
        """
        pass

class FunctionalTool(BaseTool):
    """
    A tool wrapper around a generic python function.
    """
    def __init__(self, name: str, description: str, func: Callable):
        super().__init__(name, description)
        self.func = func

    async def execute(self, **kwargs) -> Any:
        return await self.func(**kwargs)
