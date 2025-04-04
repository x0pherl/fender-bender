from unittest.mock import patch
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader

from bender_config import BenderConfig
from frame_connector import ConnectorFrame
from frame_config import FrameConfig


class TestBareExecution:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("build123d.export_stl"),
        ):
            loader = SourceFileLoader("__main__", "src/frame_connector.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )


class TestFrameConfig:
    def test_default_config(self):
        config = FrameConfig()
        assert config.stl_folder == "NONE"


class TestConnectorFrame:
    def test_none_export(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("build123d.export_stl"),
        ):
            bender_config = BenderConfig()
            frame_config = bender_config.frame_config
            frame_config.stl_folder = "NONE"
            frame = ConnectorFrame(frame_config)
            frame.compile()
            assert frame.parts[0].part.is_valid()
            assert frame.parts[0].part.is_valid()
            frame.export_stls()

    def test_default_config(self):
        frame = ConnectorFrame()
        frame.compile()
        assert frame.parts[0].part.is_valid()
        assert frame.parts[0].part.is_valid()
