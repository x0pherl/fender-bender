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
                "pin_length": 100,
                "tolerance": 0.1,
                "height": 4,
                "tie_loop": True,
            }
        }
        pinconfig = LockPinConfig(yaml_config)
        assert pinconfig.pin_length == 100

    def test_invalid_config(self):
        with pytest.raises(ValueError):
            LockPinConfig("invalid_config")


class TestLockPin:
    def test_bare_execution(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/lock_pin.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )

    def test_lock_pin(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            bender_config = BenderConfig(
                Path(__file__).parent / "../build-configs/debug.conf"
            )
            pin = LockPin(bender_config.lock_pin_config)
            pin.compile()
            pin.export_stls()
            pin.render_2d()
