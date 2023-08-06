from abc import ABC, abstractmethod

from pydantic import BaseModel

# A place for hero


class ChestBase(BaseModel, ABC):
    @abstractmethod
    def store(self, item_key: str, item: object) -> None:
        raise NotImplementedError()

    @abstractmethod
    def take(self, item_key: str) -> object:
        raise NotImplementedError()

    @abstractmethod
    def list(self) -> list[str]:
        raise NotImplementedError()

    @abstractmethod
    def drop(self, item_key: str) -> None:
        raise NotImplementedError()
