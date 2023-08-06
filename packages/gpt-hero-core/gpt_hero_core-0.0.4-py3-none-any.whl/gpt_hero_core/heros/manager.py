from ..plugins.manager import PluginManager
from .base import HeroBase


class HeroManager(PluginManager[HeroBase]):
    namespace = HeroBase.namespace


manager = HeroManager()
