import pytest
from unittest.mock import patch
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader

from bender_config import BenderConfig
from frame_bottom import BottomFrame
from frame_config import ConnectorFrameConfig


class TestBareExecution:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("build123d.export_stl"),
        ):
            loader = SourceFileLoader("__main__", "src/frame_bottom.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )
