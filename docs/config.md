# Creating a Custom Configuration

You can generate custom builds of fender bender by modifying a file in the build-configs directory, and running build.py from the root of the project. The yaml files are somewhat self-documenting, and would allow you to generate say, a 12 filament buffer, support a new tube or connector type.

The [reference configuration](https://raw.githubusercontent.com/x0pherl/fender-bender/refs/heads/main/build-configs/reference.conf) is fairly self-documenting, with plenty of comments to guide you through what each value means.

As of the time of writing the reference BenderConfig is

```
## SEE BOTTOM FOR NOTES

######### Default Configuration #########
BenderConfig:

## MOST LIKELY preferences to adjust
# output path for generated STL files
  stl_folder: ../stl/reference

# control how many filament brackets can be loaded into the system
# for the Prusa MMU3, set to 5
  filament_count: 5
# thickness of the walls separating the filament chambers
  wall_thickness: 3
# the method of locking the frame together, can be CLIP, PIN, BOTH, or NONE
  frame_lock_style: BOTH

## General specifications
# thickness for parts bearing structural elements
  minimum_structural_thickness: 4
# thickness for parts bearing no structural elements
  minimum_thickness: 1
# if you need to enforce a certain bracket depth so you can use multiple configuration brackets
# in the same frame, you can set this to the largest number required
# set to -1 to ignore
  minimum_bracket_depth: -1

# higher numbers result in a smaller rounding radius for edges
  fillet_ratio: 4
# extra gap allowance between parts, adjust as needed for your printer
  tolerance: 0.2

## wheel specifications
  wheel:
# diameter of the wheel, increasing will add to the size of the bracket,
# but may work better with certain materials
    diameter: 70
# number of spokes on the wheel, can be adjusted to increase strength or change appearance
    spoke_count: 5
# how much "wiggle" the wheel has. increasing to mach may result in filament getting stuck between the wheel and the bracket
    lateral_tolerance: 0.6
# how much of a gap to allow between the radius of the wheel and the bracket, adjust if needed for your printer (unlikely)
    radial_tolerance: 0.2
  ## bearing details
    bearing:
      diameter: 12.1
      inner_diameter: 6.1
      shelf_diameter: 8.5
      depth: 4

## Information about the filament tube connectors
  connectors:
## default connector details
    - name: "3mmx6mm tube connector"
      threaded: False
      # file_prefix: "prefix"
      # file_suffix: "suffix"
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.4
      diameter: 6.5
      length: 6.7
## filament tube details
      tube:
        inner_diameter: 3.6
        outer_diameter: 6.5
## alternative connector details
    - name: "3mmx6mm PC6-01"
      threaded: True
      file_prefix: "alt/"
      file_suffix: "-3mmx6mm-pc6-01"
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.4
      diameter: 10.3
      length: 6.7
## alternative filament tube details
      tube:
        inner_diameter: 3.6
        outer_diameter: 6.5
## alternative connector details
    - name: "2.5mmx4mm no connector"
      threaded: False
      file_prefix: "alt/"
      file_suffix: "-2_5mmx4mm-no-connector"
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.2
      diameter: 4.1
      length: 6.7
## alternative filament tube details
      tube:
        inner_diameter: 2.6
        outer_diameter: 4.1
## alternative connector details
    - name: "2.5mmx4mm PC4-M10"
      threaded: True
      file_prefix: "alt/"
      file_suffix: "-2_5mmx4mm-pc4-m10"
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.2
      diameter: 10
      length: 6.7
## alternative filament tube details
      tube:
        inner_diameter: 2.6
        outer_diameter: 4.1
## alternative connector details
    - name: "2mmx4mm no connector"
      threaded: False
      file_prefix: "alt/"
      file_suffix: "-2mmx4mm-no-connector"
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.2
      diameter: 4.1
      length: 6.7
## alternative filament tube details
      tube:
        inner_diameter: 2.1
        outer_diameter: 4.1
## alternative connector details
    - name: "2mmx4mm PC4-M10"
      threaded: True
      file_prefix: "alt/"
      file_suffix: "-2mmx4mm-pc4-m10"
      thread_pitch: 1
      thread_angle: 30
      thread_interference: 0.2
      diameter: 10
      length: 6.7
## alternative filament tube details
      tube:
        inner_diameter: 2.1
        outer_diameter: 4.1

#how deep you want the overall assembled frame to be (needs to be large enough to fully contain the buffered filament)
  frame_chamber_depth: 370
# the sizing for the empty space of the hexagon pattern, larger numbers increase visibility and decrease the strength of the walls
  wall_window_apothem: 8
# the sizing for the bars of, larger numbers decrease visibility but increase the strength of the walls
  wall_window_bar_thickness: 1.5

  frame_tongue_depth: 4
# you may want to make the locking pin a little more loose (larger number here) to make the pin
# easier to insert and remove
  frame_lock_pin_tolerance: 0.6
# the base radius of the click lock spheres
  frame_click_sphere_radius: 1

# how far up the filament bracket to place the frame clip with the "CLIP style" frame lock
  frame_clip_depth_offset: 10

## detals for the wall bracket
  wall_bracket_screw_radius: 2.25
  wall_bracket_screw_head_radius: 4.5
  wall_bracket_screw_head_sink: 1.4
## how many interlocking elements to add to the wall bracket
  wall_bracket_post_count: 3

# m4 bolt details (for the desk bracket)
  m4_heatsink_radius: 3
  m4_heatsink_depth: 5
  m4_nut_radius: 4.3
  m4_nut_depth: 5
  m4_shaft_radius: 2.15

#### Notes ####

# generally the first four elements should be the most likely things you may wish to adjust
# I've worked to minimize the number of things directly controlled in the configuration file
# many other settings are derived from these values; calculations are in bank_config.py
# adjusting these settings with care and reason *should* result in a working part, but
# there are no guarantees.  If you encounter issues, please open an issue on the github page
```