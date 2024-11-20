from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
from bender_config import BenderConfig
from pathlib import Path

from sidewall_config import SidewallConfig
from sidewall import Sidewall


class TestConfig:
    def test_load(self):
        config_path = Path(__file__).parent / "../build-configs/dev.conf"
        if not config_path.exists() or not config_path.is_file():
            config_path = Path(__file__).parent / "../build-configs/debug.conf"

        bender_config = BenderConfig(config_path)
        sw_config = bender_config.sidewall_config
        assert isinstance(sw_config, SidewallConfig)
        assert sw_config.top_diameter == sw_config.top_radius * 2
        assert (
            sw_config.straight_length == bender_config.sidewall_straight_depth
        )
        assert sw_config.complete_length == 153.0677324554909


class TestSidewall:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("build123d.export_stl"),
        ):
            loader = SourceFileLoader("__main__", "src/sidewall.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )

    def test_double_ended_sidewall(self):
        sidewall = Sidewall()
        assert sidewall._base_sidewall_shape(end_count=2).is_valid()

    def test_none_stl_folder(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("build123d.export_stl"),
        ):
            sidewall = Sidewall()
            sidewall._config.stl_folder = "NONE"
            sidewall.export_stls()


class TestTongueGroove:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("build123d.export_stl"),
        ):
            loader = SourceFileLoader("__main__", "src/tongue_groove.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )
