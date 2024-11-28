import pytest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
from pathlib import Path

from twist_snap import (
    TwistSnapConfig,
    TwistSnapConnector,
    TwistSnapEndFinish,
    TwistSnapSection,
)
from bender_config import BenderConfig


class TestTwistSnap:
    def test_bare_execution(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/twist_snap.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )

    def test_twist_snap_complete(self):
        connector = TwistSnapConnector(
            TwistSnapConfig(
                connector_diameter=4.5,
                wall_size=2,
                tolerance=0.12,
                section=TwistSnapSection.COMPLETE,
                snapfit_height=2,
                snapfit_radius_extension=2 * (2 / 3) - 0.06,
                wall_width=2,
                wall_depth=2,
            )
        )
        connector.compile()
        assert len(connector.parts) == 2
        assert connector.parts[0].part.is_valid()
        assert connector.parts[1].part.is_valid()
