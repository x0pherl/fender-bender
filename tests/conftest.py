import sys
import os
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from bender_config import BenderConfig
from filament_wheel_config import WheelConfig, BearingConfig


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
    - name: "3mmx6mm tube connector"
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
  fill: "HEX"
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
def bender_config_yaml_threaded():
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
    - name: "3mmx6mm PC6-01"
      threaded: True
      file_prefix: "alt/"
      file_suffix: "-3mmx6mm-pc6-01"
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.4
      diameter: 10.3
      length: 6.7
      tube:
        inner_diameter: 3.6
        outer_diameter: 6.5
  frame_chamber_depth: 340
  fill: "HEX"
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
def bender_config_reference_single_connector_yaml():
    return """BenderConfig:
  stl_folder: ../stl/reference
  filament_count: 5
  wall_thickness: 3
  frame_lock_style: BOTH
  minimum_structural_thickness: 4
  minimum_thickness: 1
  minimum_bracket_depth: -1
  fillet_ratio: 4
  tolerance: 0.2
  wheel:
    diameter: 70
    spoke_count: 5
    lateral_tolerance: 0.6
    radial_tolerance: 0.2
    bearing:
      diameter: 12.1
      inner_diameter: 6.1
      shelf_diameter: 8.5
      depth: 4
  connectors:
    - name: "3mmx6mm tube connector"
      threaded: False
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.4
      diameter: 6.5
      length: 6.7
      tube:
        inner_diameter: 3.6
        outer_diameter: 6.5
  frame_chamber_depth: 370
  fill: "HEX"
  wall_window_apothem: 8
  wall_window_bar_thickness: 1.5
  frame_tongue_depth: 4
  frame_lock_pin_tolerance: 0.4
  frame_click_sphere_radius: 1
  frame_clip_depth_offset: 10
  wall_bracket_screw_radius: 2.25
  wall_bracket_screw_head_radius: 4.5
  wall_bracket_screw_head_sink: 1.4
  wall_bracket_post_count: 3
"""


@pytest.fixture
def complete_connector_config_yaml():
    return """
BenderConfig:
  stl_folder: ../stl/reference
  filament_count: 5
  wall_thickness: 3
  frame_lock_style: BOTH
  minimum_structural_thickness: 4
  minimum_thickness: 1
  minimum_bracket_depth: -1
  fillet_ratio: 4
  tolerance: 0.2
  wheel:
    diameter: 70
    spoke_count: 5
    lateral_tolerance: 0.6
    radial_tolerance: 0.2
    bearing:
      diameter: 12.1
      inner_diameter: 6.1
      shelf_diameter: 8.5
      depth: 4
  connectors:
    - name: "3mmx6mm tube connector"
      threaded: False
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.4
      diameter: 6.5
      length: 6.7
      tube:
        inner_diameter: 3.6
        outer_diameter: 6.5
    - name: "3mmx6mm PC6-01"
      threaded: True
      file_prefix: "alt/"
      file_suffix: "-3mmx6mm-pc6-01"
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.4
      diameter: 10.3
      length: 6.7
      tube:
        inner_diameter: 3.6
        outer_diameter: 6.5
    - name: "2.5mmx4mm no connector"
      threaded: False
      file_prefix: "alt/"
      file_suffix: "-2_5mmx4mm-no-connector"
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.2
      diameter: 4.1
      length: 6.7
      tube:
        inner_diameter: 2.6
        outer_diameter: 4.1
  frame_chamber_depth: 370
  fill: "HEX"
  wall_window_apothem: 8
  wall_window_bar_thickness: 1.5
  frame_tongue_depth: 4
  frame_lock_pin_tolerance: 0.4
  frame_click_sphere_radius: 1
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
    - name: "3mmx6mm tube connector"
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
  fill: "HEX"
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
    - name: "3mmx6mm tube connector"
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
  fill: "HEX"
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
def wheel_config_yaml():
    return """
wheel:
  diameter: 12.3
  spoke_count: 25
  lateral_tolerance: 1.111
  radial_tolerance: 0.222
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
  bearing: {diameter: 1.2, inner_diameter: 0.1, shelf_diameter: 0.2, depth: 1}
"""


@pytest.fixture
def wheel_config_subpath_yaml():
    return """
tree1:
  wheel:
    diameter: 12.3
    spoke_count: 25
    lateral_tolerance: 1.111
    radial_tolerance: 0.222
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


@pytest.fixture
def filament_bracket_config_yaml():
    return """
FilamentBracket:
    stl_folder: "NONE"
    file_prefix: ""
    file_suffix: ""
    wheel:
        diameter: 12.3
        spoke_count: 25
        lateral_tolerance: 1.111
        radial_tolerance: 0.222
        bearing:
            diameter: 1.2
            inner_diameter: 0.1
            shelf_diameter: 0.2
            depth: 1
    connector:
        name: "3mmx6mm tube connector"
        threaded: False
        file_prefix: "prefix"
        file_suffix: "suffix"
        thread_pitch: 1
        thread_angle: 30
        thread_interference: 0.4
        diameter: 6.5
        length: 6.7
        tube:
            inner_diameter: 3.6
            outer_diameter: 6.5
    wheel_support_height: 0.2
    bracket_depth: 12.6
    bracket_height: 43.5
    bracket_width: 96.3
    exterior_radius: 52
    frame_bracket_exterior_x_distance: 1
    fillet_radius: 3.15
    frame_click_sphere_point: (47.86, 4.15)
    frame_click_sphere_radius: 1
    frame_clip_depth_offset: 10
    frame_clip_point: (50.89, 10)
    frame_clip_rail_width: 1.41
    frame_clip_width: 15.1
    frame_lock_pin_tolerance: 0.6
    frame_lock_style: "BOTH"
    lock_pin:
        stl_folder: "NONE"
        pin_length: 100
        tolerance: 0.1
        height: 4
        tie_loop: True
    minimum_structural_thickness: 4
    minimum_thickness: 1
    sidewall_section_depth: 168
    sidewall_width: 96.1
    tolerance: 0.2
    wall_thickness: 3
    wall_window_apothem: 8
    wall_window_bar_thickness: 1.5
    bearing_shelf_height: 4.3
    channel_pair_direction: "LEAN_FORWARD"
"""


@pytest.fixture
def filament_bracket_config_yaml_with_dict():
    return """
FilamentBracket:
  stl_folder: "NONE"
  file_prefix: ""
  file_suffix: ""
  wheel:
    diameter: 12.3
    spoke_count: 25
    lateral_tolerance: 1.111
    radial_tolerance: 0.222
    bearing:
      diameter: 1.2
      inner_diameter: 0.1
      shelf_diameter: 0.2
      depth: 1
  connector:
    name: "3mmx6mm tube connector"
    threaded: False
    file_prefix: "prefix"
    file_suffix: "suffix"
    thread_pitch: 1
    thread_angle: 30
    thread_interference: 0.4
    diameter: 6.5
    length: 6.7
    tube:
      inner_diameter: 3.6
      outer_diameter: 6.5
  wheel_support_height: 0.2
  bracket_depth: 12.6
  bracket_height: 43.5
  bracket_width: 96.3
  exterior_radius: 52
  frame_bracket_exterior_x_distance: 1
  fillet_radius: 3.15
  frame_click_sphere_point: (47.86, 4.15)
  frame_click_sphere_radius: 1
  frame_clip_depth_offset: 10
  frame_clip_point: (50.89, 10)
  frame_clip_rail_width: 1.41
  frame_clip_width: 15.1
  frame_lock_pin_tolerance: 0.6
  frame_lock_style: "BOTH"
  lock_pin: {stl_folder: "NONE", pin_length: 123, tolerance: 0.1, height: 4, tie_loop: True}
  minimum_structural_thickness: 4
  minimum_thickness: 1
  sidewall_section_depth: 168
  sidewall_width: 96.1
  tolerance: 0.2
  wall_thickness: 3
  wall_window_apothem: 8
  wall_window_bar_thickness: 1.5
  bearing_shelf_height: 4.3
  channel_pair_direction: "LEAN_FORWARD"
"""
