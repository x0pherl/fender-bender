from dataclasses import dataclass, field
from enum import Enum, auto
import pytest
from unittest.mock import patch
from pathlib import Path

from partomatic import BuildablePart, Part, PartomaticConfig, Partomatic
from build123d import BuildPart, Box, Sphere, Align, Mode, Location


class FakeEnum(Enum):
    ONE = auto()
    TWO = auto()
    THREE = auto()


class SubConfig(PartomaticConfig):
    sub_field: str = "sub_default"
    sub_enum: FakeEnum = FakeEnum.ONE


class ContainerConfig(PartomaticConfig):
    container_field: str = "container_default"
    sub: SubConfig = field(default_factory=SubConfig)


class TestPartomaticConfig:
    config_yaml = """
Part:
    stl_folder: "yaml_folder"
    file_prefix: "yaml_prefix"
    file_suffix: "yaml_suffix"
"""
    blah_config_yaml = """
Foo:
    container_field: "yaml_container_field"
    Blah:
        stl_folder: "yaml_blah_folder"
        file_prefix: "yaml_blah_prefix"
        file_suffix: "yaml_blah_suffix"
        sub_field: "yaml_sub_field"
        sub_enum: "TWO"
"""

    sub_config_yaml = """
Part:
    container_field: "yaml_container_field"
    sub:
        stl_folder: "yaml_blah_folder"
        file_prefix: "yaml_blah_prefix"
        file_suffix: "yaml_blah_suffix"
        sub_field: "yaml_sub_field"
        sub_enum: "TWO"
"""

    def test_yaml_partomat(self):
        config = PartomaticConfig(self.config_yaml)
        assert config.stl_folder == "yaml_folder"

    def test_empty_partomat(self):
        config = PartomaticConfig()
        assert config.stl_folder == "NONE"

    def test_subconfig(self):
        config = SubConfig(self.blah_config_yaml, yaml_tree="Foo/Blah")
        assert config.stl_folder == "yaml_blah_folder"
        assert config.sub_field == "yaml_sub_field"
        assert config.sub_enum == FakeEnum.TWO

    def test_kwargs(self):
        config = SubConfig(yaml_tree="Part/Blah", sub_field="kwargsub")
        assert config.stl_folder == "NONE"
        assert config.sub_field == "kwargsub"

    def test_yaml_container_partomat(self):
        config = ContainerConfig(self.sub_config_yaml)
        assert config.container_field == "yaml_container_field"
        assert config.sub.sub_field == "yaml_sub_field"

    def test_invalid_config(self):
        with pytest.raises(ValueError):
            ContainerConfig("invalid_config")

    def test_yaml_container_with_dict_partomat(self):
        config = ContainerConfig(
            sub={
                "stl_folder": "yaml_blah_folder",
                "file_prefix": "yaml_blah_prefix",
                "file_suffix": "yaml_blah_suffix",
                "sub_field": "yaml_sub_field",
                "sub_enum": "TWO",
            }
        )
        assert config.sub.sub_field == "yaml_sub_field"

    def test_yaml_container_with_class_partomat(self):
        sub_config = SubConfig(self.blah_config_yaml, yaml_tree="Foo/Blah")

        config = ContainerConfig(sub=sub_config)
        assert config.sub.sub_field == "yaml_sub_field"

    def test_default_container_partomat(self):
        config = ContainerConfig()
        assert config.container_field == "container_default"
        assert config.sub.sub_field == "sub_default"

    def test_config_create(self):
        config = PartomaticConfig()
        config.stl_folder = "config_create_folder"
        config = PartomaticConfig(config)
        assert config.stl_folder == "config_create_folder"


class TestBuildablePart:
    def test_extension_removed(self):
        widget_part = Part()
        widget = BuildablePart(widget_part, "widget.stl")
        assert widget.file_name == "widget"


@dataclass
class WidgetConfig(PartomaticConfig):
    stl_folder: str = field(default="C:\\Users\\xopher\\Downloads")
    radius: float = field(default=10)
    length: float = field(default=17)


class Widget(Partomatic):

    _config: WidgetConfig = WidgetConfig()

    def compile(self):
        self.parts.clear()
        with BuildPart() as holebox:
            Box(
                self._config.length,
                self._config.length,
                self._config.length,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )
            Sphere(
                self._config.radius,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                mode=Mode.SUBTRACT,
            )

        self.parts.append(
            BuildablePart(
                holebox.part,
                "test",
                display_location=Location((9, 0, 9)),
                stl_folder=str(Path(self._config.stl_folder) / "stls"),
                step_folder=str(Path(self._config.stl_folder) / "steps"),
                create_folders=True,
            )
        )


class TestPartomatic:

    def test_partomatic_class(self):
        wc = WidgetConfig()
        assert wc.stl_folder == "C:\\Users\\xopher\\Downloads"
        foo = Widget(wc)
        assert foo._config.radius == 10
        assert foo._config.length == 17
        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("build123d.export_stl"),
            patch("build123d.export_step"),
        ):
            foo.display()
            foo.partomate()
        foo._config.stl_folder = "NONE"
        foo.export_stls()
