from dataclasses import dataclass, fields
from pathlib import Path

import yaml


@dataclass
class LockPinConfig:
    stl_folder: str = "NONE"
    pin_length: float = 100
    tolerance: float = 0.1
    height: float = 4
    tie_loop: bool = True

    def load_config(self, configuration: str, yaml_tree="lockpin"):
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

        for field in fields(LockPinConfig):
            if field.name in config_dict:
                value = config_dict[field.name]
                setattr(self, field.name, value)

    def __init__(self, configuration: str = None, **kwargs):
        if configuration:
            configuration = str(configuration)
            try:
                self.load_config(
                    configuration, kwargs.get("yaml_tree", "lockpin")
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
