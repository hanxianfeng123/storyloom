from abc import ABC, abstractmethod

from storyloom.core.contract import StageInput, StageOutput


class Stage(ABC):
    name: str = ""

    @abstractmethod
    async def execute(self, input: StageInput) -> StageOutput:
        ...
