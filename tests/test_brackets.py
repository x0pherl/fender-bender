from unittest.mock import patch
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from brackets import Brackets
from bender_config import BenderConfig


class TestBrackets:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("build123d.export_stl"),
        ):
            loader = SourceFileLoader("__main__", "src/brackets.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )

    def test_none_stl(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("build123d.export_stl"),
        ):
            brackets = Brackets()
            brackets._config.stl_folder = "NONE"
            brackets.compile()
            brackets.export_stls()

    def test_render_2d(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("build123d.export_stl"),
        ):
            brackets = Brackets(BenderConfig().frame_config)
            brackets.compile()
            brackets.render_2d()
