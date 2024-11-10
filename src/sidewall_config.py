from dataclasses import dataclass, fields
from pathlib import Path
import yaml


@dataclass
class SidewallConfig:
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

    def load_config(self, configuration: str, yaml_tree="sidewall"):
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

        for field in fields(SidewallConfig):
            if field.name in config_dict:
                value = config_dict[field.name]
                setattr(self, field.name, value)

    def __init__(self, configuration: str = None, **kwargs):
        if configuration:
            configuration = str(configuration)
            try:
                self.load_config(
                    configuration, kwargs.get("yaml_tree", "sidewall")
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
