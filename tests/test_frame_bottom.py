from unittest.mock import patch
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader

from frame_bottom import BottomFrame
from bender_config import BenderConfig
from sidewall_config import WallStyle
from frame_config import FrameStyle


class TestBareExecution:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("build123d.export_stl"),
        ):
            loader = SourceFileLoader("__main__", "src/frame_bottom.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )


class TestBottomFrame:
    def test_bottom_frame_hanging(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("build123d.export_stl"),
        ):
            cfg = BenderConfig()
            cfg.stl_folder = "NONE"
            cfg.frame_style = FrameStyle.HANGING
            frame = BottomFrame(cfg.frame_config)
            frame.compile()
            assert len(frame.parts) == 1
            assert frame.parts[0].part.is_valid

    def test_bottom_frame_standing_drybox(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("build123d.export_stl"),
        ):
            cfg = BenderConfig()
            cfg.stl_folder = "NONE"
            cfg.frame_style = FrameStyle.STANDING
            cfg.wall_style = WallStyle.DRYBOX
            frame = BottomFrame(cfg.frame_config)
            frame.compile()
            assert len(frame.parts) == 1
            assert frame.parts[0].part.is_valid

    def test_bottom_frame_hybrid(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("build123d.export_stl"),
        ):
            cfg = BenderConfig()
            cfg.stl_folder = "NONE"
            cfg.frame_style = FrameStyle.HYBRID
            frame = BottomFrame(cfg.frame_config)
            frame.compile()
            assert len(frame.parts) == 1
            assert frame.parts[0].part.is_valid

    def test_default_config(self):
        frame = BottomFrame()
        frame.compile()
