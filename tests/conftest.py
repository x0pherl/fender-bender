import sys
import os
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from filament_wheel_config import WheelConfig, BearingConfig


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
