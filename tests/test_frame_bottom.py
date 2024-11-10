from unittest.mock import patch
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader

from frame_bottom import BottomFrame
from bender_config import BenderConfig


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


class TestBottomFrame:
    def test_bottom_frame(self):
        cfg = BenderConfig()
        cfg.stl_folder = "NONE"
        frame = BottomFrame(cfg.frame_config)
        frame.compile()
        frame.export_stls()

    def test_default_config(self):
        frame = BottomFrame()
        frame.compile()
        frame.render_2d()
