import pytest
from pathlib import Path
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
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

    def test_frame_flat_sidewall_cut(self, bender_config_yaml):
        frameset = FrameSet(bender_config_yaml)
        part = frameset._frame_flat_sidewall_cut(thickness=5)

        assert part.label == "Frame Side"
        assert part.is_valid()

    def test_frame_cut_sketch(self):
        frameset = FrameSet(str(Path(__file__).parent / "pytest_bender.conf"))
        part = frameset._frame_cut_sketch()

        assert part.is_valid()

    def test_frame_arched_sidewall_cut(self):
        frameset = FrameSet(str(Path(__file__).parent / "pytest_bender.conf"))
        part = frameset._frame_arched_sidewall_cut(thickness=5)

        assert part.label == "Frame Side"
        assert part.is_valid()

    def test_straight_wall_grooves(self):
        frameset = FrameSet(str(Path(__file__).parent / "pytest_bender.conf"))
        part = frameset.straight_wall_grooves()

        assert part.is_valid()

    def test_bracket_cutblock(
        self, bender_config_reference_single_connector_yaml
    ):
        frameset = FrameSet(bender_config_reference_single_connector_yaml)
        part = frameset.bracket_cutblock()

    #     assert part.is_valid()

    def test_connector_frame(
        self, bender_config_reference_single_connector_yaml
    ):
        frameset = FrameSet(bender_config_reference_single_connector_yaml)
        part = frameset.connector_frame()
        assert part.is_valid()
        assert part.volume == 40729.486676561406

    def test_chamber_cut(self, bender_config_reference_single_connector_yaml):
        frameset = FrameSet(bender_config_reference_single_connector_yaml)
        part = frameset._chamber_cut()

        assert part.is_valid()

    def test_bottom_frame_stand_height(
        self, bender_config_reference_single_connector_yaml
    ):
        frameset = FrameSet(bender_config_reference_single_connector_yaml)
        assert frameset._bottom_frame_stand_height == 63.864535089018204

    def test_bottom_frame_stand(
        self, bender_config_reference_single_connector_yaml
    ):
        frameset = FrameSet(bender_config_reference_single_connector_yaml)
        part = frameset._bottom_frame_stand()

        assert part.is_valid()

    def test_bottom_frame_stand_sectioncut(
        self, bender_config_reference_single_connector_yaml
    ):
        frameset = FrameSet(bender_config_reference_single_connector_yaml)
        part = frameset._bottom_frame_stand_sectioncut()

        assert part.is_valid()

    def test_bottom_frame(self, bender_config_reference_single_connector_yaml):
        frameset = FrameSet(bender_config_reference_single_connector_yaml)
        part = frameset.bottom_frame()

        assert part.is_valid()

    def test_bottom_frame_hanging(
        self, bender_config_reference_single_connector_yaml
    ):
        frameset = FrameSet(bender_config_reference_single_connector_yaml)
        part = frameset.bottom_frame(frame_style=FrameStyle.HANGING)

        assert part.is_valid()

    def test_top_frame(self, bender_config_reference_single_connector_yaml):
        frameset = FrameSet(bender_config_reference_single_connector_yaml)
        part = frameset.top_frame()

        assert part.is_valid()

    def test_top_frame_hanging(
        self, bender_config_reference_single_connector_yaml
    ):
        frameset = FrameSet(bender_config_reference_single_connector_yaml)
        part = frameset.top_frame(frame_style=FrameStyle.HANGING)

        assert part.is_valid()

    def test_frames_2d_render(
        self, bender_config_reference_single_connector_yaml
    ):
        frameset = FrameSet(bender_config_reference_single_connector_yaml)
        frameset.render_2d()

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

    def test_wall_bracket(self, bender_config_reference_single_connector_yaml):
        frameset = FrameSet(bender_config_reference_single_connector_yaml)
        part = frameset.wall_bracket()

        assert part.is_valid()

    def test_wall_hanger_bare_execution(self):
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
