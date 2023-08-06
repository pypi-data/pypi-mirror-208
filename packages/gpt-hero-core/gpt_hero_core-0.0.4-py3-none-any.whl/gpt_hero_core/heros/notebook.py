from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from gpt_hero_core.heros.schema import Clue


class NoteBookBase(BaseModel, ABC):
    # VectorStore

    @abstractmethod
    def write(self, message: str, meta: dict[str, Any]) -> Clue:
        raise NotImplementedError()

    @abstractmethod
    def search(self, query: str) -> list[Clue]:
        """Return a list of messages that match the query"""
        raise NotImplementedError()

    @abstractmethod
    def think(self, query: str) -> str:
        """Return a summary of messages that match the query"""
        raise NotImplementedError()

    @abstractmethod
    def delete(self, id: str) -> None:
        """Delete a message by id"""
        raise NotImplementedError()
