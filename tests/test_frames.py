import pytest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
from walls_config import WallsConfig
from frames import FrameSet, FrameStyle


class TestFrames:
    def test_bare_execution(self):
        with patch("build123d.export_stl"):
            with patch("pathlib.Path.mkdir"):
                with patch("ocp_vscode.show"):
                    with patch("ocp_vscode.save_screenshot"):
                        loader = SourceFileLoader("__main__", "src/frames.py")
                        loader.exec_module(
                            module_from_spec(
                                spec_from_loader(loader.name, loader)
                            )
                        )

    def test_bare_execution(self):
        with patch("build123d.export_stl"):
            with patch("pathlib.Path.mkdir"):
                with patch("ocp_vscode.show"):
                    with patch("ocp_vscode.save_screenshot"):
                        loader = SourceFileLoader(
                            "__main__", "src/wall_hanger_cut_template.py"
                        )
                        loader.exec_module(
                            module_from_spec(
                                spec_from_loader(loader.name, loader)
                            )
                        )
