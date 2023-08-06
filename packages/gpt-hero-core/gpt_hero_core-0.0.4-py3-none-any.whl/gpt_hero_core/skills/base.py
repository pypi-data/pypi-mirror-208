import typing
from abc import abstractmethod

from pydantic import validate_arguments

from ..plugins.base import _PluginBase


class SkillBase(_PluginBase):
    namespace = "skill"

    @property
    def description(self) -> str:
        """Returns the description of the skill."""
        return str(typing.get_type_hints(self.use))

    def run(self, *args: typing.Any, **kwargs: typing.Any) -> str:
        try:
            return str(validate_arguments(self.use)(*args, **kwargs))
        except Exception as e:
            return str(e)

    @abstractmethod
    def use(self, *args: typing.Any, **kwargs: typing.Any) -> str:
        raise NotImplementedError()
