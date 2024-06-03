"""
module for all of the configuration required to build a filament bank
"""
from dataclasses import dataclass

@dataclass
class BankConfig:
    """
    A dataclass for configuration values for our filament bank
    """
    bearing_diameter: float = 12
    bearing_inner_diameter = 6.1
    bearing_shelf_diameter = 8.5
    bearing_depth: float = 4

    wheel_diameter:float = 95
    spoke_count: int = 5
    wheel_lateral_tolerance: float = 0.4
    wheel_radial_tolerance: float = 0.2

    minimum_structural_thickness = 4
    minimum_thickness = 1

    connector_diameter: float = 10.1
    connector_length: float = 6.7
    connector_thread_pitch:float = 1
    connector_thread_angle:float = 30

    tube_inner_diameter = 3.5
    tube_outer_diameter = 6.5

    fillet_ratio = 4

    @property
    def bearing_shelf_radius(self):
        """
        returns the radius of the bearing shelf
        """
        return self.bearing_shelf_diameter/2
    
    @property
    def wheel_radius(self):
        """
        returns the radius of the wheel
        """
        return self.wheel_diameter/2

    @property
    def bearing_radius(self):
        """
        returns the radius of the bearing
        """
        return self.bearing_diameter/2

    @property
    def bearing_inner_radius(self):
        """
        returns the inner_radius of the bearing
        """
        return self.bearing_inner_diameter/2

    @property
    def connector_radius(self):
        """
        returns the radius of the connector
        """
        return self.connector_diameter/2

    @property
    def tube_inner_radius(self):
        """
        returnes the inner radius of the tube
        """
        return self.tube_inner_diameter/2

    @property
    def tube_outer_radius(self):
        """
        returnes the outer radius of the tube
        """
        return self.tube_outer_diameter/2

    @property
    def rim_thickness(self):
        """
        returns the thickness of the rim
        """
        return self.bearing_depth

    @property
    def bracket_width(self):
        """
        returns the width of the bracket
        """
        return self.wheel_diameter+self.minimum_structural_thickness*4+self.fillet_radius*2

    @property
    def bracket_height(self):
        """
        returns the height of the bracket
        """
        return self.wheel_radius+self.wheel_radial_tolerance+self.minimum_structural_thickness*2

    @property
    def bracket_depth(self):
        """
        returns the depth of the bracket
        """
        return max(self.bearing_depth+self.wheel_lateral_tolerance*2 + \
                   self.minimum_structural_thickness*2,
                   self.connector_diameter+self.minimum_thickness*2)

    @property
    def fillet_radius(self):
        """
        returns the fillet radis for bracket parts
        """
        return self.bracket_depth/self.fillet_ratio
