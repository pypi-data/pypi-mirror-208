from enum import Enum
from enum import IntEnum
from pdb import set_trace

from ..Traits import Trait


class Unit:
    class Type(Enum):
        INFANTRY = 1
        ARTILLERT = 2
        CAVALRY = 3
        AERIAL = 4

    class Experience(IntEnum):
        LEVIES = 1
        REGULAR = 2
        VETERAN = 3
        ELITE = 4
        SUPER_ELITE = 5

    class Equipment(IntEnum):
        LIGHT = 1
        MEDIUM = 2
        HEAVY = 3
        SUPER_HEAVY = 4

    def __init__(self, name: str, description: str, type: Type):
        self.name = name
        self.description = description
        self.battles = 0
        self.traits = []
        self.type = type
        self.experience = Unit.Experience.REGULAR
        self.equipment = Unit.Equipment.LIGHT
        self.damage = 1
        self.attacks = 1

    def clone(self) -> "Unit":
        clonedUnit = Unit(self.name, self.description, self.type)

        return clonedUnit

    def __eq__(self, __value: "Unit") -> bool:
        matches = self.name == __value.name
        matches = matches and self.description == __value.description
        matches = matches and self.battles == __value.battles
        matches = matches and self.type == __value.type
        return matches

    def add_trait(self, trait: Trait):
        if len(self.traits) < 5:
            self.traits.append(trait)
        else:
            raise Exception("This unit already has 4 traits!")

    def battle(self):
        self.battles = self.battles + 1
        if self.experience != Unit.Experience.LEVIES:
            if self.battles == 1 or self.battles == 4 or self.battles == 8:
                self.level_up()

    def upgrade(self):
        if self.experience == Unit.Experience.LEVIES:
            raise CannotUpgradeError("Cannot upgrade Levies")
        if self.equipment == Unit.Equipment.SUPER_HEAVY:
            raise CannotUpgradeError("Cannot upgrade equipment past super-heavy.")
        self.equipment = self.equipment + 1

    def level_up(self):
        if self.experience == Unit.Experience.LEVIES:
            raise CannotLevelUpError("Cannot level up levies.")
        if self.experience == Unit.Experience.SUPER_ELITE:
            raise CannotLevelUpError("Cannot level up a unit past Super-elite.")
        self.experience = self.experience + 1

    def level_down(self):
        if self.experience == Unit.Experience.LEVIES:
            raise CannotLevelUpError("Cannot level down levies.")
        if self.experience == Unit.Experience.REGULAR:
            raise CannotLevelUpError("Cannot lower level below regular.")
        self.experience = self.experience - 1


class CannotUpgradeError(Exception):
    pass


class CannotLevelUpError(Exception):
    pass
