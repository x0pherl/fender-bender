import pytest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
from pathlib import Path

from lock_pin import LockPin
from lock_pin_config import LockPinConfig
from bender_config import BenderConfig


class TestLockPinConfig:
    def test_lock_pin_yaml_load(self):
        yaml_config = {
            "lockpin": {
                "stl_folder": "NONE",
                "pin_length": 123,
                "tolerance": 0.1,
                "height": 4,
                "tie_loop": True,
            }
        }
        pinconfig = LockPinConfig(yaml_config)
        assert pinconfig.pin_length == 123

    def test_invalid_config(self):
        with pytest.raises(ValueError):
            LockPinConfig("invalid_config")


class TestLockPin:
    def test_bare_execution(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/lock_pin.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )

    def test_bare_execution_missing_file(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
            patch("pathlib.Path.exists", return_value=False),
        ):
            with pytest.raises(ValueError):
                loader = SourceFileLoader("__main__", "src/lock_pin.py")
                loader.exec_module(
                    module_from_spec(spec_from_loader(loader.name, loader))
                )

    def test_lock_pin(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            bender_config = BenderConfig()
            pin = LockPin(bender_config.lock_pin_config)
            pin._config.stl_folder = "NONE"
            pin.compile()
            pin.export_stls()

    def test_lock_pin_default_init(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            pin = LockPin()
            pin.compile()
            pin.export_stls()

    def test_lock_pin_inited(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            pin = LockPin(
                configuration={
                    "lockpin": {
                        "stl_folder": "NONE",
                        "pin_length": 123,
                        "tolerance": 0.1,
                        "height": 4,
                        "tie_loop": True,
                    }
                },
                yaml_tree="lockpin",
            )
            pin.compile()
            pin.export_stls()
