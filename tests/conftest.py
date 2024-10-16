import sys
import os
import pytest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from bender_config import BenderConfig
from filament_wheel_config import WheelConfig, BearingConfig
from walls_config import WallsConfig


# @pytest.fixture
# def mock_path_exists():
#     config_path = Path(__file__).parent / "../build-configs/dev.conf"
#     with patch.object(config_path, "exists", return_value=False):
#         yield


@pytest.fixture
def bender_config_yaml():
    return """
BenderConfig:
  stl_folder: ../stl/test
  filament_count: 6
  wall_thickness: 0.2
  frame_lock_style: BOTH
  minimum_structural_thickness: 2
  minimum_thickness: 0.2
  minimum_bracket_depth: 3
  fillet_ratio: 10
  tolerance: 0.2
  wheel:
    diameter: 20
    spoke_count: 4
    lateral_tolerance: 1.1
    radial_tolerance: 0.3
    bearing:
      diameter: 7
      inner_diameter: 5
      shelf_diameter: 6
      depth: 1
  connectors:
    - name: "3mmx6mmm tube connector"
      threaded: False
      # file_prefix: "prefix"
      # file_suffix: "suffix"
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.4
      diameter: 6.5
      length: 6.7
      tube:
        inner_diameter: 3.6
        outer_diameter: 6.5
  frame_chamber_depth: 340
  solid_walls: False
  wall_window_apothem: 8
  wall_window_bar_thickness: 1.5
  frame_tongue_depth: 4
  frame_lock_pin_tolerance: 0.4
  frame_click_sphere_radius: .05
  frame_clip_depth_offset: 10
  wall_bracket_screw_radius: 2.25
  wall_bracket_screw_head_radius: 4.5
  wall_bracket_screw_head_sink: 1.4
  wall_bracket_post_count: 3
"""


@pytest.fixture
def bender_config_yaml_default_second():
    return """
BenderConfig:
  stl_folder: ../stl/test
  filament_count: 6
  wall_thickness: 0.2
  frame_lock_style: BOTH
  minimum_structural_thickness: 2
  minimum_thickness: 0.2
  minimum_bracket_depth: 3
  fillet_ratio: 10
  tolerance: 0.2
  wheel:
    diameter: 20
    spoke_count: 4
    lateral_tolerance: 1.1
    radial_tolerance: 0.3
    bearing:
      diameter: 7
      inner_diameter: 5
      shelf_diameter: 6
      depth: 1
  connectors:
    - name: "3mmx6mmm tube connector"
      threaded: False
      # file_prefix: "prefix"
      # file_suffix: "suffix"
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.4
      diameter: 6.5
      length: 6.7
      tube:
        inner_diameter: 3.6
        outer_diameter: 6.5
    - name: "default"
      threaded: False
      # file_prefix: "prefix"
      # file_suffix: "suffix"
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.4
      diameter: 6.5
      length: 6.7
      tube:
        inner_diameter: 3.6
        outer_diameter: 1234
  frame_chamber_depth: 340
  solid_walls: False
  wall_window_apothem: 8
  wall_window_bar_thickness: 1.5
  frame_tongue_depth: 4
  frame_lock_pin_tolerance: 0.4
  frame_click_sphere_radius: .05
  frame_clip_depth_offset: 10
  wall_bracket_screw_radius: 2.25
  wall_bracket_screw_head_radius: 4.5
  wall_bracket_screw_head_sink: 1.4
  wall_bracket_post_count: 3
"""


@pytest.fixture
def bender_config_yaml_tube_dict():
    return """
BenderConfig:
  stl_folder: ../stl/test
  filament_count: 6
  wall_thickness: 0.2
  frame_lock_style: BOTH
  minimum_structural_thickness: 2
  minimum_thickness: 0.2
  minimum_bracket_depth: 3
  fillet_ratio: 10
  tolerance: 0.2
  wheel:
    diameter: 20
    spoke_count: 4
    lateral_tolerance: 1.1
    radial_tolerance: 0.3
    bearing:
      diameter: 7
      inner_diameter: 5
      shelf_diameter: 6
      depth: 1
  connectors:
    - name: "3mmx6mmm tube connector"
      threaded: False
      # file_prefix: "prefix"
      # file_suffix: "suffix"
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.4
      diameter: 6.5
      length: 6.7
      tube: {inner_diameter: 3.6, outer_diameter: 4321}
  frame_chamber_depth: 340
  solid_walls: False
  wall_window_apothem: 8
  wall_window_bar_thickness: 1.5
  frame_tongue_depth: 4
  frame_lock_pin_tolerance: 0.4
  frame_click_sphere_radius: .05
  frame_clip_depth_offset: 10
  wall_bracket_screw_radius: 2.25
  wall_bracket_screw_head_radius: 4.5
  wall_bracket_screw_head_sink: 1.4
  wall_bracket_post_count: 3
"""


@pytest.fixture
def default_bender_config() -> BenderConfig:
    return BenderConfig()


@pytest.fixture
def wall_config_yaml():
    return """
walls:
    top_diameter: 70
    top_extension: 10
    sidewall_width: 110
    wall_thickness: 3
    reinforcement_thickness: 7
    section_depth: 170
"""


@pytest.fixture
def wall_config():
    cfg = WallsConfig()
    return cfg


@pytest.fixture
def wheel_config_yaml():
    return """
wheel:
  diameter: 12.3
  spoke_count: 25
  lateral_tolerance: 1.111
  radial_tolerance: 0.222
  stl_folder: ./stls
  bearing:
    diameter: 1.2
    inner_diameter: 0.1
    shelf_diameter: 0.2
    depth: 1
"""


@pytest.fixture
def wheel_config_bearing_dict_yaml():
    return """
wheel:
  diameter: 12.3
  spoke_count: 25
  lateral_tolerance: 1.111
  radial_tolerance: 0.222
  stl_folder: ./stls
  bearing: {diameter: 1.2, inner_diameter: 0.1, shelf_diameter: 0.2, depth: 1}
"""


@pytest.fixture
def wheel_config_subpath_yaml():
    return """
tree1:
  tree2:
    wheel:
      diameter: 12.3
      spoke_count: 25
      lateral_tolerance: 1.111
      radial_tolerance: 0.222
      stl_folder: ./stls
      bearing:
        diameter: 1.2
        inner_diameter: 0.1
        shelf_diameter: 0.2
        depth: 1
"""


@pytest.fixture
def wheel_config():
    cfg = WheelConfig()
    return cfg


@pytest.fixture
def bearing_config():
    cfg = BearingConfig()
    return cfg
