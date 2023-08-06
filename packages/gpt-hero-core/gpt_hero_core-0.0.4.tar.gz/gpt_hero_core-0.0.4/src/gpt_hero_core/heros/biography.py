from abc import ABC, abstractmethod

from pydantic import BaseModel

from .schema import Action, ActionType


class BiographyBase(BaseModel, ABC):
    # NOTE:
    # It is Message History
    @abstractmethod
    def act(self, action_type: ActionType, message: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def read(self, action_type: ActionType = None, limit: int = 10, newest: bool = True) -> list[Action]:
        raise NotImplementedError()
