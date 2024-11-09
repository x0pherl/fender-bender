from unittest.mock import patch
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader

from bender_config import BenderConfig
from frame_connector import ConnectorFrame
from frame_config import ConnectorFrameConfig


class TestBareExecution:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("build123d.export_stl"),
        ):
            loader = SourceFileLoader("__main__", "src/frame_connector.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )


class TestConnectorFrameConfig:
    def test_default_config(self):
        config = ConnectorFrameConfig()
        assert config.stl_folder == "NONE"


class TestConnectorFrame:
    def test_none_export(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("build123d.export_stl"),
        ):
            bender_config = BenderConfig()
            frame_config = bender_config.connector_frame_config
            frame_config.stl_folder = "NONE"
            frame = ConnectorFrame(frame_config)
            frame.compile()
            assert frame._hanging_frame.is_valid()
            assert frame._standing_frame.is_valid()
            frame.export_stls()
            frame.render_2d()

    def test_default_config(self):
        frame = ConnectorFrame()
        frame.compile()
        assert frame._hanging_frame.is_valid()
        assert frame._standing_frame.is_valid()
