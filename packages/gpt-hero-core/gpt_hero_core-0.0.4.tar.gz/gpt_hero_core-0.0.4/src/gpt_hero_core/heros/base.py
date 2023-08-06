from abc import abstractmethod

from gpt_hero_core.heros.biography import BiographyBase
from gpt_hero_core.heros.chest import ChestBase
from gpt_hero_core.heros.mission import MissionBase
from gpt_hero_core.heros.notebook import NoteBookBase

from ..plugins.base import _PluginBase
from ..skills.base import SkillBase


class HeroBase(_PluginBase):
    namespace = "hero"

    skills: list[SkillBase] = []

    # for hero to store items, unlink memory, there is no index
    chest: ChestBase | None = None
    biography: BiographyBase | None = None
    notebook: NoteBookBase | None = None
    mission: MissionBase | None = None

    @abstractmethod
    def turn(self, message: str) -> str:
        raise NotImplementedError()
