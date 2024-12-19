from dataclasses import dataclass, fields
from enum import Enum, auto
from pathlib import Path
import yaml

from partomatic import PartomaticConfig


class WallStyle(Enum):
    SOLID = auto()
    DRYBOX = auto()
    HEX = auto()


class SidewallConfig(PartomaticConfig):
    yaml_tree: str = "sidewall"
    stl_folder: str = "../stl/default"
    top_diameter: float = 70
    top_extension: float = 10
    straight_length: float = 125
    sidewall_width: float = 110
    wall_thickness: float = 3
    minimum_thickness: float = 1
    reinforcement_thickness: float = 7
    reinforcement_inset: float = 7
    wall_window_apothem: float = 8
    wall_window_bar_thickness: float = 1.5
    click_fit_radius: float = 1
    end_count: int = 1
    wall_style: WallStyle = WallStyle.HEX
    block_inner_wall_generation: bool = False

    @property
    def top_radius(self) -> float:
        """
        the radius of the top of the wall
        """
        return self.top_diameter / 2

    @property
    def complete_length(self) -> float:
        """
        the total height of the sidewall
        """
        return self.straight_length + (
            (self.top_radius + self.top_extension) * self.end_count
        )
