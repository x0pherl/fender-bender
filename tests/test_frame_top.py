from unittest.mock import patch
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader

from bender_config import BenderConfig
from frame_top import TopFrame


class TestBareExecution:
    def test_bare_execution(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/frame_top.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )


class TestTopFrame:
    def test_top_frame(self, bender_config_reference_single_connector_yaml):
        bender_config = BenderConfig(
            bender_config_reference_single_connector_yaml
        )
        frame = TopFrame(bender_config.frame_config)
        part = frame.top_frame()
        assert part.is_valid()
