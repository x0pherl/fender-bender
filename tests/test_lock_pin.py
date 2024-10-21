import pytest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
from pathlib import Path

from lock_pin import LockPin


class TestLockPin:
    def test_bare_execution(self):
        with patch("build123d.export_stl"):
            with patch("pathlib.Path.mkdir"):
                with patch("ocp_vscode.show"):
                    with patch("ocp_vscode.save_screenshot"):
                        loader = SourceFileLoader(
                            "__main__", "src/lock_pin.py"
                        )
                        loader.exec_module(
                            module_from_spec(
                                spec_from_loader(loader.name, loader)
                            )
                        )

    def test_lock_pin(self):
        pin = LockPin(Path(__file__).parent / "../build-configs/debug.conf")
        pin._config.stl_folder = "NONE"
        pin.export_stls()
        pin.compile()
        pin.render_2d()
