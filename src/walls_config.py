from dataclasses import dataclass
from enum import Enum, auto

from bender_config import BenderConfig


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

    def load_from_bender_config(self, bender_config: BenderConfig):
        self.top_diameter = (
            bender_config.wheel.diameter - bender_config.wall_thickness
        )
        self.top_extension = bender_config.frame_bracket_spacing
        self.sidewall_width = bender_config.sidewall_width
        self.wall_thickness = bender_config.sidewall_straight_depth
        self.reinforcement_thickness = bender_config.frame_connector_depth
        self.section_depth = bender_config.frame_bracket_exterior_radius
        return self
