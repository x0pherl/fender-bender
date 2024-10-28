import pytest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
from filament_channels import FilamentChannels
from filament_bracket import FilamentBracket


class TestFilamentBracket:
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
                        bracket.compile()
                        bracket.display()
                        bracket.export_stls()
                        bracket._config.stl_folder = "c:/temp"
                        bracket.export_stls()
                        bracket.render_2d(save_to_disk=True)

    def test_bracket_block(self):
        bracket = FilamentBracket()
        block = bracket.bottom_bracket_block()
        assert block is not None
        assert block.volume > 0
        assert block.bounding_box().size.X == 106.66585530967899

    def test_straight_filament_path(self):
        channels = FilamentChannels()
        path = channels.straight_filament_path()
        assert path is not None
        assert path.volume > 0
        assert path.bounding_box().size.X == 12.600000000000001

    def test_curved_filament_path(self):
        channels = FilamentChannels()
        path = channels.curved_filament_path()
        assert path is not None
        assert path.volume > 0
        assert path.bounding_box().size.X == 26.203270321667198

    def test_initialized_load(self, bender_config_yaml_threaded):
        channels = FilamentChannels(bender_config_yaml_threaded)
        assert channels._config.default_connector.thread_angle == 30

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

    def test_channels_bare_execution(self):
        loader = SourceFileLoader("__main__", "src/filament_channels.py")
        loader.exec_module(
            module_from_spec(spec_from_loader(loader.name, loader))
        )
