from abc import ABC
from importlib.metadata import EntryPoint
from typing import ClassVar

import pydantic


class _PluginBase(pydantic.BaseModel, ABC):
    namespace: ClassVar[str] = "root"
    name: ClassVar[str]

    @classmethod
    def entrypoint(cls) -> EntryPoint:
        return EntryPoint(
            name=cls.name,
            value=f"{cls.__module__}:{cls.__name__}",
            group=cls.namespace,
        )
