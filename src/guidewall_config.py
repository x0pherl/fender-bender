from dataclasses import dataclass, fields
from pathlib import Path
import yaml

from partomatic import PartomaticConfig
from sidewall_config import WallStyle


class GuidewallConfig(PartomaticConfig):
    stl_folder: str = "../stl/default"
    core_length: float = 125
    section_width: float = 110
    section_count: int = 5
    wall_thickness: float = 3
    minimum_thickness: float = 1
    tongue_width: float = 350
    tongue_depth: float = 3
    reinforcement_thickness: float = 7
    reinforcement_inset: float = 4
    wall_window_apothem: float = 8
    wall_window_bar_thickness: float = 1.5
    click_fit_radius: float = 1
    click_fit_distance: float = 61
    tolerance: float = 0.2
    fillet_ratio: float = 4.0
    wall_style: WallStyle = WallStyle.HEX

    @property
    def width(self) -> float:
        """
        the total width of the guidewall
        """
        return (
            self.section_width * self.section_count
            + self.reinforcement_thickness * 2
        )

    @property
    def rail_length(self) -> float:
        """
        the length of the guiderails, allowing for tolerances
        """
        return self.core_length - self.tolerance * 2
