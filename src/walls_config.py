from dataclasses import dataclass
from enum import Enum, auto


class SidewallShape(Enum):
    """What sort of shape to generate to have"""

    BASE = auto()
    POINT = auto()
    REINFORCEMENT = auto()


@dataclass
class WallsConfig:
    top_diameter: float = 70
    top_extension: float = 10
    sidewall_width: float = 110
    wall_thickness: float = 3
    reinforcement_thickness: float = 7

    section_depth: float = 170

    @property
    def top_radius(self) -> float:
        """
        the radius of the top of the wall
        """
        return self.top_diameter / 2

    @property
    def sidewall_straight_length(self) -> float:
        """
        the length of the straight portion of the sidewall
        """
        return self.section_depth - self.top_radius - self.top_extension
