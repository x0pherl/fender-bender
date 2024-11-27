from unittest.mock import patch
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from hanging_bracket import HangingBracket
from hanging_bracket_config import HangingBracketStyle
from bender_config import BenderConfig


class TestBrackets:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("build123d.export_stl"),
        ):
            loader = SourceFileLoader("__main__", "src/hanging_bracket.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )

    def test_hanging_bracket(self):
        bracket = HangingBracket()
        assert bracket._config is not None
        bracket._config.bracket_style = HangingBracketStyle.WALL_MOUNT
        bracket.compile()
        assert len(bracket.parts) == 1
        assert bracket.parts[0].part.is_valid()

    def test_desk_bracket_nut(self):
        bracket = HangingBracket()
        bracket._config.bracket_style = HangingBracketStyle.SURFACE_MOUNT
        bracket._config.heatsink_desk_nut = False
        bracket.compile()
        assert len(bracket.parts) == 1
        assert bracket.parts[0].part.is_valid()

    def test_desk_bracket_nut(self):
        bracket = HangingBracket()
        bracket._config.bracket_style = HangingBracketStyle.SURFACE_MOUNT
        bracket._config.heatsink_desk_nut = True
        bracket.compile()
        assert len(bracket.parts) == 1
        assert bracket.parts[0].part.is_valid()

    def test_desk_bracket(self):
        bracket = HangingBracket()
        bracket._config.bracket_style = HangingBracketStyle.SURFACE_TOOL
        bracket.compile()
        assert len(bracket.parts) == 1
        assert bracket.parts[0].part.is_valid()

    def test_none_stl(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            bracket = HangingBracket()
            bracket._config.stl_folder = "NONE"
            bracket.compile()
            bracket.export_stls()


class TestCutTemplate:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("build123d.export_stl"),
        ):
            loader = SourceFileLoader(
                "__main__", "src/wall_hanger_cut_template.py"
            )
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )
