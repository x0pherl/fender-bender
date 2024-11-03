from dataclasses import dataclass, fields
import yaml
from pathlib import Path


@dataclass
class TopFrameConfig:
    stl_folder: str
    exterior_width: float
    exterior_length: float
    depth: float
    interior_length: float
    interior_width: float
    interior_offset: float
    fillet_radius: float
    bracket_spacing: float
    bracket_width: float
    filament_count: int
    wall_thickness: float
    tolerance: float
    groove_width: float
    groove_depth: float
    groove_distance: float
    click_fit_radius: float
    base_depth: float
    bracket_height: float
    exterior_radius: float
    interior_radius: float
    base_depth: float
    bracket_height: float
    exterior_radius: float
    interior_radius: float
    tube_radius: float
    minimum_structural_thickness: float
    include_lock_clip: bool = True
    include_lock_pin: bool = True
    cut_hanger: bool = True
    wall_bracket_post_count: int = 3
    lock_pin_tolerance: float = 0.5
    screw_head_radius: float = 4.5
    screw_head_sink: float = 1.4
    screw_shaft_radius: float = 2.25

    @property
    def bracket_depth(self) -> float:
        return self.bracket_spacing - self.wall_thickness - self.tolerance * 2

    @property
    def exterior_diameter(self) -> float:
        return self.exterior_radius * 2

    @property
    def interior_diameter(self) -> float:
        return self.interior_radius * 2

    def load_config(self, configuration: str, yaml_tree="top-frame"):
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

        for field in fields(TopFrameConfig):
            if field.name in config_dict:
                value = config_dict[field.name]
                setattr(self, field.name, value)

    def __init__(self, configuration: str = None, **kwargs):
        if configuration:
            configuration = str(configuration)
            try:
                self.load_config(
                    configuration, kwargs.get("yaml_tree", "top-frame")
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
class BottomFrameConfig(TopFrameConfig):
    pass


@dataclass
class ConnectorFrameConfig:
    stl_folder: str = "NONE"
    exterior_width: float = 50
    exterior_length: float = 200
    depth: float = 10
    interior_length: float = 180
    interior_width: float = 30
    interior_offset: float = 4
    fillet_radius: float = 2
    bracket_spacing: float = 30
    filament_count: int = 1
    wall_thickness: float = 2
    tolerance: float = 0.2
    groove_width: float = 1
    groove_depth: float = 2
    groove_distance: float = 1
    click_fit_radius: float = 1

    def load_config(self, configuration: str, yaml_tree="connector-frame"):
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

        for field in fields(ConnectorFrameConfig):
            if field.name in config_dict:
                value = config_dict[field.name]
                setattr(self, field.name, value)

    def __init__(self, configuration: str = None, **kwargs):
        if configuration:
            configuration = str(configuration)
            try:
                self.load_config(
                    configuration, kwargs.get("yaml_tree", "connector-frame")
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
