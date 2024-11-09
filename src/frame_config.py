from dataclasses import dataclass, fields
import yaml
from pathlib import Path


@dataclass
class FrameConfig:
    stl_folder: str = "NONE"
    exterior_width: float = 91
    exterior_length: float = 120
    depth: float = 9
    interior_length: float = 90.1
    interior_width: float = 77
    interior_offset: float = 2
    fillet_radius: float = 3.15
    bracket_spacing: float = 16
    bracket_width: float = 96.3
    filament_count: int = 5
    wall_thickness: float = 3
    tolerance: float = 0.2
    groove_width: float = 3.2
    groove_depth: float = 4.2
    groove_distance: float = 99.1
    click_fit_radius: float = 1
    base_depth: float = 8
    bracket_height: float = 43.2
    exterior_radius: float = 51.86
    interior_radius: float = 35
    tube_radius: float = 3.25
    minimum_structural_thickness: float = 4
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

    def load_config(self, configuration: str, yaml_tree="frame"):
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

        for field in fields(FrameConfig):
            if field.name in config_dict:
                value = config_dict[field.name]
                setattr(self, field.name, value)

    def __init__(self, configuration: str = None, **kwargs):
        if configuration:
            configuration = str(configuration)
            try:
                self.load_config(
                    configuration, kwargs.get("yaml_tree", "frame")
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
