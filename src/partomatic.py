"""Part extended for CI/CD automation"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields, is_dataclass, MISSING
from enum import Enum, Flag
from pathlib import Path
from typing import Type, Any
from os import getcwd

from build123d import Part, Location, export_stl, export_step

# from ocp_vscode import show, Camera
import ocp_vscode

import yaml


@dataclass
class PartomaticConfig:
    stl_folder: str = "NONE"
    file_prefix: str = ""
    file_suffix: str = ""
    create_folders_if_missing: bool = True
    yaml_tree: str = "Part"

    def _default_config(self):
        """
        Resets all values to their default values.
        """
        for field in fields(self):
            if field.default is not MISSING:
                setattr(self, field.name, field.default)
            elif field.default_factory is not MISSING:
                setattr(self, field.name, field.default_factory())
            else:
                raise ValueError(f"Field {field.name} has no default value")

    def load_config(self, configuration: any, yaml_tree="Part"):
        """
        loads a partomatic configuration from a file or valid yaml
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
        -------
        notes:
            if yaml_tree is set in the PartomaticConfig descendent,
            PartomaticConfig will use that tree to find a node deep
            within the yaml tree, following the node names separated by slashes
            (example: "BigObject/Partomatic")
        """
        self.yaml_tree = yaml_tree
        if isinstance(configuration, self.__class__):
            for field in fields(self):
                setattr(self, field.name, getattr(configuration, field.name))
            return

        configuration = str(configuration)
        if "\n" not in configuration:
            path = Path(configuration)
            if path.exists() and path.is_file():
                configuration = path.read_text()
        bracket_dict = yaml.safe_load(configuration)
        for node in self.yaml_tree.split("/"):
            if node not in bracket_dict:
                raise ValueError(
                    f"Node {node} not found in configuration file"
                )
            bracket_dict = bracket_dict[node]

        for classfield in fields(self.__class__):
            if classfield.name in bracket_dict:
                value = bracket_dict[classfield.name]
                if isinstance(classfield.type, type) and issubclass(
                    classfield.type, (Enum, Flag)
                ):
                    setattr(
                        self, classfield.name, classfield.type[value.upper()]
                    )
                elif is_dataclass(classfield.type) and isinstance(value, dict):
                    setattr(
                        self,
                        classfield.name,
                        classfield.type(**value),
                    )
                else:
                    setattr(self, classfield.name, value)

    def __init__(self, configuration: any = None, **kwargs):
        """
        loads a partomatic configuration from a file or valid yaml
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
                OR
              None (default) for an empty object
            - **kwargs: specific fields to set in the configuration
        -------
        notes:
            you can assign yaml_tree as a kwarg here to load a
            configuration from a node node deep within the yaml tree,
            following the node names separated by slashes
            (example: "BigObject/Partomatic")
        """
        if "yaml_tree" in kwargs:
            self.yaml_tree = kwargs["yaml_tree"]
        if configuration is not None:
            self.load_config(configuration, yaml_tree=self.yaml_tree)
        elif kwargs:
            self._default_config()
            for key, value in kwargs.items():
                classfield = next(
                    (f for f in fields(self.__class__) if f.name == key),
                    None,
                )
                if classfield:
                    if is_dataclass(classfield.type):
                        if isinstance(value, dict):
                            setattr(self, key, classfield.type(**value))
                        else:
                            setattr(self, key, value)
                    else:
                        setattr(self, key, value)
        else:
            self._default_config()


@dataclass
class BuildablePart(Part):
    part: Part
    display_location: Location = field(default_factory=Location)
    stl_folder: str = getcwd()
    # step_folder: str = getcwd()
    _file_name: str = "partomatic"

    def __init__(self, part, file_name, **kwargs):
        self.display_location = Location()
        self.file_name = file_name
        self.part = part
        if "display_location" in kwargs:
            display_location = kwargs["display_location"]
            if isinstance(display_location, Location):
                self.display_location = display_location
        # if "step_folder" in kwargs:
        #     self.step_folder = kwargs["step_folder"]
        if "stl_folder" in kwargs:
            self.stl_folder = kwargs["stl_folder"]

    @property
    def file_name(self) -> str:
        return self._file_name

    @file_name.setter
    def file_name(self, value: str):
        """
        Assigns the file name to the BuildablePart, ensuring that no
        file extension is included.
        """
        self._file_name = Path(value).stem


class Partomatic(ABC):
    """
    Partomatic is an extension of the Compound class from build123d
    that allows for automation within a continuous integration
    environment. Descendant classes must implement:
    - compile: generating the geometry of components in the parts list
    """

    _config: PartomaticConfig
    parts: list[BuildablePart] = field(default_factory=list)

    @abstractmethod
    def compile(self):
        """
        Builds the relevant parts for the partomatic part
        """

    def display(self):
        """
        Shows the relevant parts in OCP CAD Viewer
        """
        ocp_vscode.show(
            (
                [
                    part.part.move(Location(part.display_location))
                    for part in self.parts
                ]
            ),
            reset_camera=ocp_vscode.Camera.KEEP,
        )

    def complete_stl_file_path(self, part: BuildablePart) -> str:
        return str(
            Path(
                Path(part.stl_folder)
                / f"{self._config.file_prefix}{part.file_name}{self._config.file_suffix}"
            ).with_suffix(".stl")
        )

    def complete_step_file_path(self, part: BuildablePart) -> str:
        return str(
            Path(
                Path(part.step_folder)
                / f"{self._config.file_prefix}{part.file_name}{self._config.file_suffix}"
            ).with_suffix(".step")
        )

    def export_stls(self):
        """
        Generates the relevant STLs in the configured
        folder
        """
        if self._config.stl_folder == "NONE":
            return
        for part in self.parts:
            Path(self.complete_stl_file_path(part)).parent.mkdir(
                parents=True, exist_ok=self._config.create_folders_if_missing
            )
            if (
                not Path(self.complete_stl_file_path(part)).parent.exists()
                or not Path(self.complete_stl_file_path(part)).parent.is_dir()
            ):
                raise FileNotFoundError(
                    f"Directory {Path(self.complete_stl_file_path(part)).parent} does not exist"
                )
            export_stl(part.part, self.complete_stl_file_path(part))

        # def export_steps(self):
        #     """
        #     Generates the relevant STEPs in the configured
        #     folder
        #     """
        # if self._config.step_folder == "NONE":
        #     return

        # for part in self.parts:
        #     Path(self.complete_step_file_path(part)).parent.mkdir(
        #         parents=True, exist_ok=self._config.create_folders_if_missing
        #     )
        #     if (
        #         not Path(self.complete_step_file_path(part)).parent.exists()
        #         or not Path(self.complete_step_file_path(part)).parent.is_dir()
        #     ):
        #         raise FileNotFoundError(
        #             f"Directory {Path(self.complete_step_file_path(part)).parent} does not exist"
        #         )
        #     export_step(part.part, self.complete_step_file_path(part))

    def load_config(self, configuration: any, yaml_tree="Part", **kwargs):
        """
        loads a partomatic configuration from a file or valid yaml
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
        -------
        notes:
            if yaml_tree is set in the PartomaticConfig descendent,
            PartomaticConfig will use that tree to find a node deep
            within the yaml tree, following the node names separated by slashes
            (example: "BigObject/Partomatic")
        """
        self._config.load_config(configuration, yaml_tree)

    # def __init_subclass__(cls, **kwargs):
    #     super().__init_subclass__(**kwargs)
    #     if not hasattr(cls, "_config") or not issubclass(
    #         cls._config.__class__, PartomaticConfig
    #     ):
    #         raise TypeError(
    #             f"{cls.__name__} must define a '_config' attribute that is a PartomaticConfig or a subclass of PartomaticConfig"
    #         )

    def __init__(self, configuration: any = None, **kwargs):
        """
        loads a partomatic configuration from a file or valid yaml
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
                OR
              None (default) for an empty object
            - **kwargs: specific fields to set in the configuration
        -------
        notes:
            you can assign yaml_tree as a kwarg here to load a
            configuration from a node node deep within the yaml tree,
            following the node names separated by slashes
            (example: "BigObject/Partomatic")
        """
        self.parts = []
        self.load_config(configuration, **kwargs)
        print(self._config)

    def partomate(self):
        """automates the part generation and exports stl and step models
         -------
        notes:
            - if you want to avoid exporting one of those file formats,
              you can override the export_stls or export_steps methods
              with a no-op method using the pass keyword
        """
        self.compile()
        self.export_stls()
        # self.export_steps()
