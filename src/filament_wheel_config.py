import yaml
from dataclasses import dataclass, field, fields
from pathlib import Path


@dataclass
class BearingConfig:
    diameter: float = 12.1
    inner_diameter: float = 6.1
    shelf_diameter: float = 8.5
    depth: float = 4

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

    def __init__(self, **kwargs):
        for field in fields(self):
            setattr(self, field.name, kwargs.get(field.name, field.default))


@dataclass
class WheelConfig:
    diameter: float = 70
    spoke_count: int = 5
    lateral_tolerance: float = 0.6
    radial_tolerance: float = 0.2
    bearing: BearingConfig = field(default_factory=BearingConfig)
    stl_folder: str = ""

    @property
    def radius(self) -> float:
        """
        returns the radius of the wheel
        """
        return self.diameter / 2

    def load_config(self, configuration: str, yaml_tree="wheel"):
        """
        loads a wheel configuration from a file or valid yaml
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
            - yaml_tree: the yaml tree to the wheel configuration node,
            separated by slashes (example: "BenderConfig/wheel")
        """
        configuration = str(configuration)
        if "\n" not in configuration:
            path = Path(configuration)
            if path.exists() and path.is_file():
                configuration = path.read_text()
        wheel_dict = yaml.safe_load(configuration)
        for node in yaml_tree.split("/"):
            wheel_dict = wheel_dict[node]

        for field in fields(WheelConfig):
            if field.name in wheel_dict:
                value = wheel_dict[field.name]
                if field.name == "bearing":
                    self.bearing = BearingConfig(**value)
                else:
                    setattr(self, field.name, value)

    def __init__(self, configuration: str = None, **kwargs):
        if configuration:
            configuration = str(configuration)
            try:
                self.load_config(
                    configuration, kwargs.get("yaml_tree", "wheel")
                )
            except Exception as e:
                raise ValueError(
                    f"Error loading configuration from {configuration}: {e}"
                ) from e
        else:
            for field in fields(self):
                if field.name == "bearing":
                    config_value = kwargs.get(field.name, field.default)
                    if isinstance(config_value, dict):
                        self.bearing = BearingConfig(**config_value)
                    else:
                        self.bearing = BearingConfig()
                else:
                    setattr(
                        self, field.name, kwargs.get(field.name, field.default)
                    )
