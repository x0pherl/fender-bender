from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
import pytest
from filament_channels import FilamentChannels
from filament_bracket import FilamentBracket
from bender_config import BenderConfig
from filament_bracket_config import FilamentBracketConfig


class TestFilamentBracket:
    def test_bare_execution(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/filament_bracket.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )

    def test_complete_connector_set(self, complete_connector_config_yaml):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("filament_bracket.save_screenshot"),
        ):
            bender_config = BenderConfig(complete_connector_config_yaml)
            bracket = FilamentBracket(bender_config.filament_bracket_config())
            bracket.compile()
            bracket.display()
            bracket.export_stls()
            bracket._config.stl_folder = "c:/temp"
            bracket.export_stls()

    def test_bracket_block(self):
        bender_config = BenderConfig()
        bracket = FilamentBracket(bender_config.filament_bracket_config())
        block = bracket.bottom_bracket_block()
        assert block is not None
        assert block.volume > 0
        assert block.bounding_box().size.X == pytest.approx(106.20623590190772)

    def test_straight_filament_path(self):
        channels = FilamentChannels()
        block = channels.straight_filament_block_solid()
        assert block is not None
        assert block.is_valid
        path = channels.straight_filament_path_cut()
        assert path is not None
        assert block.is_valid

    def test_curved_filament_path(self):
        channels = FilamentChannels()
        block = channels.curved_filament_block_solid()
        assert block is not None
        assert block.is_valid
        path = channels.curved_filament_path_cut()
        assert path is not None
        assert block.is_valid

    def test_initialized_load_from_bender_config(
        self, bender_config_yaml_threaded
    ):
        bender_config = BenderConfig(bender_config_yaml_threaded)
        channels = FilamentChannels(bender_config.filament_bracket_config())
        assert channels._config.connector.thread_angle == 30

    def test_bare_execution(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/filament_bracket.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )

    def test_channels_bare_execution(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/filament_channels.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )


class TestFilamentBracketConfig:

    def test_detault_config(self):
        config = FilamentBracketConfig()
        config.bracket_height = 1000
        assert config.bracket_height == 1000
        config._default_config()
        assert config.bracket_height == pytest.approx(43.5)

    def test_yaml_config(self, filament_bracket_config_yaml):
        config = FilamentBracketConfig(filament_bracket_config_yaml)
        assert config.bracket_height == pytest.approx(43.5)

    def test_yaml_with_dict_config(
        self, filament_bracket_config_yaml_with_dict
    ):
        config = FilamentBracketConfig(filament_bracket_config_yaml_with_dict)
        assert config.lock_pin.pin_length == pytest.approx(123)

    def test_dict_kwargs(self, filament_bracket_config_yaml_with_dict):
        config = FilamentBracketConfig(
            lock_pin={
                "stl_folder": "NONE",
                "pin_length": 123,
                "tolerance": 0.1,
                "height": 4,
                "tie_loop": True,
            }
        )
        assert config.lock_pin.pin_length == pytest.approx(123)
