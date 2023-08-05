from enum import Enum

class HLDDirection(str, Enum):
    """
    Enum with all* HLD directions.
    """
    def __str__(self):
        return self.value
    NORTH = "North"
    EAST = "East"
    WEST = "West"
    SOUTH = "South"
    CENTRAL = "Central"
    INTRO = "Intro"
    ABYSS = "Abyss"
