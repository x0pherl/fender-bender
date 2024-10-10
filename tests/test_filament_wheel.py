import pytest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path
from build123d import Part

from filament_wheel_config import WheelConfig, BearingConfig
from filament_wheel import FilamentWheel, diamond_torus


class TestConfig:

    def test_wheelconfig_radius(self, wheel_config):
        assert wheel_config.radius == wheel_config.diameter / 2
        assert wheel_config.bearing.radius == wheel_config.bearing.diameter / 2
        assert (
            wheel_config.bearing.inner_radius
            == wheel_config.bearing.inner_diameter / 2
        )
        assert (
            wheel_config.bearing.shelf_radius
            == wheel_config.bearing.shelf_diameter / 2
        )

    def test_wheelconfig_defaults(self, wheel_config):
        assert (
            wheel_config.diameter
            == WheelConfig.__dataclass_fields__["diameter"].default
        )

    def test_wheelconfig_load_yaml_str(self, wheel_config_yaml):
        cfg = WheelConfig(configuration=wheel_config_yaml)
        assert cfg.diameter == 12.3
        assert cfg.spoke_count == 25
        assert cfg.lateral_tolerance == 1.111
        assert cfg.radial_tolerance == 0.222
        assert cfg.stl_folder == "./stls"
        assert cfg.bearing.diameter == 1.2
        assert cfg.bearing.inner_diameter == 0.1
        assert cfg.bearing.shelf_diameter == 0.2
        assert cfg.bearing.depth == 1

    def test_wheelconfig_load_bearing_dict_yaml_str(
        self,
        wheel_config_bearing_dict_yaml,
    ):
        cfg = WheelConfig(configuration=wheel_config_bearing_dict_yaml)
        assert cfg.bearing.diameter == 1.2
        assert cfg.bearing.inner_diameter == 0.1
        assert cfg.bearing.shelf_diameter == 0.2
        assert cfg.bearing.depth == 1

    def test_wheelconfig_load_subpath_yaml_str(
        self, wheel_config_subpath_yaml
    ):
        cfg = WheelConfig(
            configuration=wheel_config_subpath_yaml,
            yaml_tree="tree1/tree2/wheel",
        )
        assert cfg.diameter == 12.3
        assert cfg.spoke_count == 25
        assert cfg.lateral_tolerance == 1.111
        assert cfg.radial_tolerance == 0.222
        assert cfg.stl_folder == "./stls"
        assert cfg.bearing.diameter == 1.2
        assert cfg.bearing.inner_diameter == 0.1
        assert cfg.bearing.shelf_diameter == 0.2
        assert cfg.bearing.depth == 1

    def test_missing_wheel_config_file(self):
        with pytest.raises(ValueError):
            WheelConfig(configuration="missing_file.yaml")

    def test_load_wheel_config_file(self):
        config_path = Path(__file__).parent / "pytest_wheel.conf"

        cfg = WheelConfig(configuration=config_path)
        assert cfg.diameter == 12.3
        assert cfg.spoke_count == 25
        assert cfg.lateral_tolerance == 1.111
        assert cfg.radial_tolerance == 0.222
        assert cfg.stl_folder == "./stls"
        assert cfg.bearing.diameter == 1.2
        assert cfg.bearing.inner_diameter == 0.1
        assert cfg.bearing.shelf_diameter == 0.2
        assert cfg.bearing.depth == 1


class TestTorus:
    def test_diamond_torus(self):
        torus = diamond_torus(major_radius=10, minor_radius=1)
        assert isinstance(torus, Part)
        assert torus.bounding_box().size.X == 22


class TestWheel:
    def test_partomate(self, wheel_config):
        fw = FilamentWheel(wheel_config)
        fw.partomate()
        assert fw.wheel.volume > 0

    def test_loadconfig(self, wheel_config, wheel_config_subpath_yaml):
        fw = FilamentWheel()
        fw.load_config(
            wheel_config_subpath_yaml, yaml_tree="tree1/tree2/wheel"
        )
        assert fw._config.diameter == 12.3

    def test_display(self):
        fw = FilamentWheel()
        fw.compile()
        fw.display()

    def test_uncompiled_display(self):
        fw = FilamentWheel()
        with pytest.raises(AttributeError):
            fw.display()

    def test_NONE_export(self):
        fw = FilamentWheel()
        fw._config.stl_folder = "NONE"
        fw.export_stls()

    def test_bare_execution(self):
        loader = SourceFileLoader("__main__", "src/filament_wheel.py")
        loader.exec_module(
            module_from_spec(spec_from_loader(loader.name, loader))
        )
