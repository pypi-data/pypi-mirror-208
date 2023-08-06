from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel

from .schema import Task, TaskStatus


class MissionBase(BaseModel, ABC):
    goal: str
    description: str

    status: TaskStatus = TaskStatus.TODO

    @abstractmethod
    def expand(self, sub_task: Task, parent: Task | None = None) -> None:
        """add a sub task to the mission"""
        raise NotImplementedError()

    @abstractmethod
    def complete(self, task: Task, message: str | None = None) -> None:
        """complete a task"""
        raise NotImplementedError()

    @abstractmethod
    def skip(self, task: Task, message: str | None = None) -> None:
        """skip a task"""
        raise NotImplementedError()

    @abstractmethod
    def mark(self, task: Task) -> None:
        """mark a task as doing"""
        raise NotImplementedError()

    @abstractmethod
    def summary(self) -> str:
        """summary of the mission"""
        raise NotImplementedError()

    @abstractmethod
    def list_all(self) -> list[Task]:
        """list all tasks"""
        raise NotImplementedError()

    @abstractmethod
    def list_sub_tasks(self, parent: Task) -> list[Task]:
        """list sub tasks"""
        raise NotImplementedError()
