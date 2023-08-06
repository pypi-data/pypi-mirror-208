from ..plugins.manager import PluginManager
from .base import SkillBase


class SkillManager(PluginManager[SkillBase]):
    namespace = SkillBase.namespace


manager = SkillManager()
