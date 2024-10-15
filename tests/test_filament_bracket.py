import pytest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
from walls_config import WallsConfig
from filament_bracket import FilamentBracket


class TestFrames:
    def test_bare_execution(self):
        with patch("build123d.export_stl"):
            with patch("pathlib.Path.mkdir"):
                with patch("ocp_vscode.show"):
                    with patch("ocp_vscode.save_screenshot"):
                        loader = SourceFileLoader(
                            "__main__", "src/filament_bracket.py"
                        )
                        loader.exec_module(
                            module_from_spec(
                                spec_from_loader(loader.name, loader)
                            )
                        )

    # def test_bare_execution_with_missing_file(self):
    #     with patch("build123d.export_stl"):
    #         with patch("pathlib.Path.mkdir"):
    #             with patch("ocp_vscode.show"):
    #                 with patch("ocp_vscode.save_screenshot"):
    #                     with patch("pathlib.Path.exists", return_value=False):
    #                         loader = SourceFileLoader(
    #                             "__main__", "src/filament_bracket.py"
    #                         )
    #                         loader.exec_module(
    #                             module_from_spec(
    #                                 spec_from_loader(loader.name, loader)
    #                             )
    #                         )

    def test_complete_connector_set(self, complete_connector_config_yaml):
        with patch("build123d.export_stl"):
            with patch("pathlib.Path.mkdir"):
                with patch("ocp_vscode.show"):
                    with patch("ocp_vscode.save_screenshot"):
                        bracket = FilamentBracket(
                            complete_connector_config_yaml
                        )
                        bracket._config.stl_folder = "NONE"
                        bracket.compile()
                        bracket.display()
                        bracket.export_stls()
                        bracket.render_2d(save_to_disk=True)
