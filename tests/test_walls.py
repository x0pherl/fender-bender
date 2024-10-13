import pytest
from walls_config import WallsConfig


class TestWallConfig:
    def test_wall_config(self, wall_config):
        assert wall_config.top_diameter == 70
        assert wall_config.top_extension == 10
        assert wall_config.sidewall_width == 110
        assert wall_config.wall_thickness == 3
        assert wall_config.reinforcement_thickness == 7
        assert wall_config.section_depth == 170
