from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ActionType(str, Enum):
    ACT = "ACT"
    CHAT = "CHAT"


class Action(BaseModel):
    type: ActionType
    message: str


class Clue(BaseModel):
    id: str
    message: str


class TaskStatus(str, Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    SKIP = "skip"
    WAITING = "waiting"


class Task(BaseModel):
    goal: str
    description: str
    message: str | None

    parent: Task | None = None
    status: TaskStatus = TaskStatus.TODO
