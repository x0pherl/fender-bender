import yaml
from dataclasses import dataclass, field, fields
from pathlib import Path

from partomatic import PartomaticConfig


@dataclass
class BearingConfig(PartomaticConfig):
    diameter: float = 12.1
    inner_diameter: float = 6.1
    shelf_diameter: float = 8.5
    depth: float = 4
    print_in_place: bool = False

    @property
    def radius(self) -> float:
        """
        returns the radius of the bearing
        """
        return self.diameter / 2

    @property
    def inner_radius(self) -> float:
        """
        returns the inner_radius of the bearing
        """
        return self.inner_diameter / 2

    @property
    def shelf_radius(self) -> float:
        """
        returns the radius of the bearing shelf
        """
        return self.shelf_diameter / 2

    def __init__(self, configuration: any = None, **kwargs):
        super().__init__(configuration, **kwargs)


@dataclass
class WheelConfig(PartomaticConfig):
    yaml_tree = "wheel"
    diameter: float = 70
    spoke_count: int = 5
    lateral_tolerance: float = 0.6
    radial_tolerance: float = 0.2
    bearing: BearingConfig = field(default_factory=BearingConfig)

    @property
    def radius(self) -> float:
        """
        returns the radius of the wheel
        """
        return self.diameter / 2

    @property
    def depth(self) -> float:
        """returns the depth of the bearing"""
        return self.bearing.depth

    def __init__(self, configuration: any = None, **kwargs):
        super().__init__(configuration, **kwargs)
