from dataclasses import dataclass, fields
from pathlib import Path

import yaml


@dataclass
class GuidewallConfig:
    stl_folder: str = "../stl/default"
    core_length: float = 125
    section_width: float = 110
    section_count: int = 5
    wall_thickness: float = 3
    tongue_width: float = 350
    tongue_depth: float = 3
    reinforcement_thickness: float = 7
    reinforcement_inset: float = 4
    solid_wall: bool = False
    wall_window_apothem: float = 8
    wall_window_bar_thickness: float = 1.5
    click_fit_radius: float = 1
    tolerance: float = 0.2
    fillet_ratio: float = 4.0

    @property
    def width(self) -> float:
        """
        the total width of the guidewall
        """
        return (
            self.section_width * self.section_count
            + self.reinforcement_thickness * 2
        )

    def load_config(self, configuration: str, yaml_tree="guidewall"):
        """
        loads a configuration from a file or valid yaml
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
        """
        configuration = str(configuration)
        if "\n" not in configuration:
            path = Path(configuration)
            if path.exists() and path.is_file():
                configuration = path.read_text()
        config_dict = yaml.safe_load(configuration)
        for node in yaml_tree.split("/"):
            config_dict = config_dict[node]

        for field in fields(GuidewallConfig):
            if field.name in config_dict:
                value = config_dict[field.name]
                setattr(self, field.name, value)

    def __init__(self, configuration: str = None, **kwargs):
        if configuration:
            configuration = str(configuration)
            try:
                self.load_config(
                    configuration, kwargs.get("yaml_tree", "guidewall")
                )
            except Exception as e:
                raise ValueError(
                    f"Error loading configuration from {configuration}: {e}"
                ) from e
        else:
            for field in fields(self):
                setattr(
                    self, field.name, kwargs.get(field.name, field.default)
                )
