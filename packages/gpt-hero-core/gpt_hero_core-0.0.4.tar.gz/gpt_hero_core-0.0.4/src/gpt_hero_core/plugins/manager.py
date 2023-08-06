import enum
from importlib.metadata import EntryPoint
from typing import Any, ClassVar, Generic, TypeVar

from pydantic.generics import GenericModel
from stevedore import DriverManager, _cache, exception

from . import base

T = TypeVar("T", bound=base._PluginBase)


class PluginManager(GenericModel, Generic[T]):
    namespace: ClassVar[str] = "root"

    def init_plugin_by_name(self, name: str | enum.Enum, *args: Any, **kwargs: Any) -> T:
        """
        Init plugin instance by name, it will only load the matched plugin.
        :param name: driver name
        :param args: plugin args
        :param kwargs: plugin kwargs
        :return: plugin
        """
        return self.get_plugin_by_name(name)(*args, **kwargs)

    def get_plugin_by_name(self, name: str | enum.Enum) -> type[T]:
        """
        Get plugin class by name, it will only load the matched plugin.
        :param name: driver name
        :return: plugin class
        """
        if isinstance(name, enum.Enum):
            name = str(name.value)

        try:
            manager = DriverManager(self.namespace, name, invoke_on_load=False)
        except exception.NoMatches as e:
            raise ValueError(f"Cannot find plugin {name} in namespace {self.namespace}") from e

        return manager.driver

    def all_plugin_names(self) -> list[str]:
        """
        Get all driver names directly from entrypoints, it won't load any plugin
        :return: plugin names
        """
        output: list[str] = []

        entry_point: EntryPoint
        for entry_point in _cache.get_group_all(self.namespace):
            output.append(entry_point.name)

        return output
