"""
Generates the part for the frames connecting the walls and holding the
filament brackets in place
"""
from build123d import (BuildPart, BuildSketch, Part, Cylinder, extrude,
                       Mode, add, Location, loft, fillet, Axis, Box,
                       Align, GridLocations, Plane, Sphere, GeomType,
                       Circle, Locations, export_stl,
                       PolarLocations)
from ocp_vscode import show, Camera
from bank_config import BankConfig
from basic_shapes import rounded_cylinder,frame_side_cut,frame_side_flat_cut
from wall_cut_template import wall_cut_template
from filament_bracket import bottom_bracket_block, bracket_clip

config = BankConfig()

def flat_wall_grooves() -> Part:
    """
    creates the grooves in the frame peices for the front and back walls
    """
    with BuildPart(mode=Mode.PRIVATE) as groove:
        Box(config.wall_thickness+config.frame_bracket_tolerance,
            config.top_frame_interior_width+config.frame_bracket_tolerance,
            config.frame_tongue_depth-config.wall_thickness/2+config.frame_bracket_tolerance,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        extrude(groove.faces().sort_by(Axis.Z)[-1], amount=config.wall_thickness/2, taper=44)
        with BuildPart(groove.faces().sort_by(Axis.X)[-1], mode=Mode.ADD):
            with GridLocations(0,config.top_frame_interior_width/1.5,1,2):
                Sphere(radius=config.frame_click_sphere_radius)
        with BuildPart(groove.faces().sort_by(Axis.X)[0], mode=Mode.SUBTRACT):
            with GridLocations(0,config.top_frame_interior_width/1.5,1,2):
                Sphere(radius=config.frame_click_sphere_radius*.75)
        with BuildPart(mode=Mode.SUBTRACT):
            Box(config.wall_thickness+config.frame_bracket_tolerance, config.wall_thickness/2,
                    config.frame_tongue_depth+config.frame_bracket_tolerance,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
            with BuildPart(Location((0,0,config.wall_thickness))):
                Sphere(radius=config.wall_thickness*.5)

    with BuildPart() as grooves:
        with PolarLocations(-config.sidewall_width/2-config.wall_thickness/2,2):
            add(groove.part.mirror())
    return grooves.part

def bracket_cutblock() -> Part:
    """
    the block that needs to be cut for each filament bracket in the top frame
    """
    with BuildPart() as cutblock:
        add(bottom_bracket_block(offset=config.frame_bracket_tolerance).rotate(
            Axis.X, 90).move(Location((0,config.bracket_depth/2+config.frame_bracket_tolerance,
                                    config.frame_base_depth))))
        with BuildPart(Location((-config.wheel_radius-config.bracket_depth/2,0,config.frame_base_depth))) as boxcut:
            Box(config.bracket_width*2,
                config.bracket_depth+config.frame_bracket_tolerance*2,
                config.bracket_height*2,
                align=(Align.MIN, Align.CENTER, Align.MIN)
                )
        with BuildPart(Location((0,0,config.frame_base_depth))) as boxcut:
            Cylinder(radius=config.wheel_radius + \
                    config.wheel_radial_tolerance+config.connector_diameter+config.fillet_radius,
                    height=config.bracket_depth+config.frame_bracket_tolerance*2,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),rotation=(90,0,0))
            fillet(boxcut.edges(), radius=config.fillet_radius)

        with BuildPart(Location((0,0,config.frame_base_depth+config.frame_bracket_tolerance),(0,-config.frame_clip_angle,0))):
            with GridLocations(0,config.bracket_depth+config.frame_bracket_tolerance*2,1,2):
                Box(config.wheel_diameter*4,config.wall_thickness*2/3-config.frame_bracket_tolerance,
                    config.wall_thickness*2+config.frame_bracket_tolerance,
                    align=(Align.MIN,Align.CENTER,Align.MAX))
    return cutblock.part

def chamber_cut() -> Part:
    """
    a filleted box for each chamber in the lower connectors
    """
    with BuildPart() as chamber_cut:
        Box(config.sidewall_width-config.wall_thickness,
                config.bracket_depth+config.frame_bracket_tolerance*2,
                config.bracket_height*3,
                align=(Align.CENTER, Align.CENTER, Align.CENTER)
                )
        fillet(chamber_cut.edges(), radius=config.fillet_radius)
    return chamber_cut.part

def connector_frame() -> Part:
    """
    the connecting frame for supporting the walls of the top and extension
    sections
    """
    with BuildPart() as cframe:
        with BuildPart(Location((-config.minimum_structural_thickness/2,0,0))):
            Box(config.frame_bracket_exterior_diameter+config.minimum_structural_thickness*3,
                config.frame_exterior_width,
                config.connector_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
        fillet(cframe.edges(), config.fillet_radius)
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(cframe.faces().sort_by(Axis.Z)[-1],
                           cframe.faces().sort_by(Axis.Z)[0]):
                add(flat_wall_grooves())
                with GridLocations(0,config.bracket_depth+config.frame_bracket_tolerance*2+config.wall_thickness,1,config.filament_count+1):
                    add(frame_side_flat_cut())
            with BuildPart(Location((-config.minimum_structural_thickness/2,0,0))):
                with GridLocations(0,config.bracket_depth+config.frame_bracket_tolerance*2+config.wall_thickness,1,config.filament_count):
                    add(chamber_cut())
    return cframe.part

def bottom_frame() -> Part:
    """
    the bottom frame for supporting the walls
    """

    with BuildPart() as bframe:
        with BuildPart(Location((-config.minimum_structural_thickness/2,0,0))):
            Box(config.frame_bracket_exterior_diameter+config.minimum_structural_thickness*3,
                config.frame_exterior_width,
                config.frame_base_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(Location((0,0,config.frame_base_depth))) as top_arch:
            Cylinder(radius=config.frame_bracket_exterior_radius,
                 height=config.frame_exterior_width,
                 rotation=(90,0,0), arc_size=180,
                 align=(Align.CENTER,Align.MIN,Align.CENTER))
        edge_set=bframe.edges()-bframe.edges().filter_by_position(Axis.X,
                minimum=config.frame_bracket_exterior_radius-1,
                maximum=config.frame_bracket_exterior_radius+1) - \
                bframe.edges().filter_by_position(Axis.X,
                minimum=-config.frame_bracket_exterior_radius-1,
                maximum=-config.frame_bracket_exterior_radius+1)
        fillet(edge_set,config.fillet_radius)
        with BuildPart(mode=Mode.SUBTRACT):
            with GridLocations(0,config.bracket_depth+config.frame_bracket_tolerance*2+config.wall_thickness,1,config.filament_count):
                add(chamber_cut())
            with GridLocations(0,config.bracket_depth+config.frame_bracket_tolerance*2+config.wall_thickness,1,config.filament_count+1):
                add(frame_side_cut())
            with BuildPart(Location((0,0,config.frame_base_depth))):
                Cylinder(radius=config.wheel_radius,
                        height=config.frame_exterior_width,
                        rotation=(90,0,0))
            add(flat_wall_grooves().mirror(Plane.XY))
    return bframe.part

def top_frame() -> Part:
    """
    the top frame for fitting the filament brackets and hanging the walls
    """
    with BuildPart() as tframe:
        Box(config.frame_bracket_exterior_diameter+config.minimum_structural_thickness*2,
            config.frame_exterior_width,
            config.frame_base_depth,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        Box(config.frame_bracket_exterior_radius+config.minimum_structural_thickness*2,
            config.frame_exterior_width,
            config.bracket_height,
            align=(Align.MAX, Align.CENTER, Align.MIN))
        with BuildPart(Location((0,0,config.frame_base_depth))) as top_arch:
            Cylinder(radius=config.frame_bracket_exterior_radius,
                 height=config.frame_exterior_width,
                 rotation=(90,0,0), arc_size=180,
                 align=(Align.CENTER,Align.MIN,Align.CENTER))
        edge_set=tframe.edges()-tframe.edges().filter_by_position(Axis.X,
                minimum=config.frame_bracket_exterior_radius-1,
                maximum=config.frame_bracket_exterior_radius+1)
        fillet(edge_set,config.fillet_radius)
        with BuildPart(mode=Mode.SUBTRACT):
            with GridLocations(0,config.bracket_depth+config.frame_bracket_tolerance*2+config.wall_thickness,1,config.filament_count):
                add(bracket_cutblock())
            with GridLocations(0,config.bracket_depth+config.frame_bracket_tolerance*2+config.wall_thickness,1,config.filament_count+1):
                add(frame_side_cut())
            with BuildPart(Location((0,0,config.frame_base_depth))):
                Cylinder(radius=config.wheel_radius,
                        height=config.frame_exterior_width,
                        rotation=(90,0,0))
                Box(config.wheel_diameter, config.frame_exterior_width,
                        config.frame_base_depth,
                        align=(Align.CENTER,Align.CENTER, Align.MAX)
                    )
            add(flat_wall_grooves().mirror(Plane.XY))

        with BuildPart(Location((-config.frame_bracket_exterior_radius,0,config.bracket_depth+config.minimum_structural_thickness),(0,90,0))):
            with GridLocations(0,config.bracket_depth+config.frame_bracket_tolerance*2+config.wall_thickness,1,config.filament_count):
                with GridLocations(0,config.bracket_depth+config.frame_bracket_tolerance*2, 1,2):
                    add(rounded_cylinder(radius=config.wall_thickness-config.frame_bracket_tolerance, height=config.bracket_depth,align=
                            (Align.CENTER, Align.CENTER, Align.MIN)))

        with BuildPart(Location((config.frame_click_sphere_point.x,0,config.frame_click_sphere_point.y+config.frame_base_depth))):
            with GridLocations(0,config.bracket_depth+config.frame_bracket_tolerance*2+config.wall_thickness,1,config.filament_count):
                with GridLocations(0,config.bracket_depth+config.frame_bracket_tolerance*2, 1,2):
                    Sphere(config.frame_click_sphere_radius*.75)

        if config.frame_wall_bracket:
            with BuildPart(Location((-config.frame_bracket_exterior_radius-config.minimum_structural_thickness*1.25,0,0)), mode=Mode.SUBTRACT):
                add(wall_cut_template(config.minimum_structural_thickness*1.5,config.frame_exterior_width,config.bracket_height,bottom=False, post_count=config.wall_bracket_post_count, tolerance=config.frame_bracket_tolerance))


    return tframe.part

def wall_bracket() -> Part:
    with BuildPart() as bracket:
        Box(config.minimum_structural_thickness*3,config.frame_exterior_width,config.spoke_depth+config.spoke_bar_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
        fillet(bracket.edges(), config.minimum_structural_thickness/config.fillet_ratio)
        with BuildPart(mode=Mode.INTERSECT):
            add(wall_cut_template(config.minimum_structural_thickness*1.5,config.frame_exterior_width,config.bracket_height,bottom=True, post_count=config.wall_bracket_post_count, tolerance=config.frame_bracket_tolerance))
        with BuildPart(Location((config.minimum_structural_thickness/3,0,(config.spoke_depth+config.spoke_bar_height)/2),(0,-90,0)), mode=Mode.SUBTRACT):
            add(screw_head())
    return bracket.part

def screw_head() -> Part:
    with BuildPart() as head:
        with BuildSketch():
            Circle(config.wall_bracket_screw_head_radius)
        with BuildSketch(Plane.XY.offset(1.4)):
            Circle(config.wall_bracket_screw_head_radius)
        with BuildSketch(Plane.XY.offset(1.4+config.wall_bracket_screw_head_radius-config.wall_bracket_screw_radius)):
            Circle(config.wall_bracket_screw_radius)
        with BuildSketch(Plane.XY.offset(config.frame_back_foot_length)):
            Circle(config.wall_bracket_screw_radius)
        loft(ruled=True)
    return head.part
    #wall_bracket_screw_radius = 2.25
    #wall_bracket_screw_head_radius=4.5


if __name__ == '__main__':
    bracketclip = bracket_clip()
    topframe = top_frame()
    bottomframe = bottom_frame()
    connectorframe = connector_frame()
    wallbracket = wall_bracket()
    export_stl(bracketclip, '../stl/bracket_clip.stl')
    export_stl(topframe, '../stl/top_frame.stl')
    export_stl(bottomframe, '../stl/bottom_frame.stl')
    export_stl(connectorframe, '../stl/connector_frame.stl')
    export_stl(wallbracket, '../stl/wall_bracket.stl')
    show(topframe,
        bracketclip.rotate(Axis.X,180).move(Location((config.fillet_radius,0,0))).rotate(Axis.Y,-config.frame_clip_angle).move(Location((0,0,config.frame_base_depth))),
        bottomframe.rotate(axis=Axis.X,angle=180).move(Location((0,0,
            -config.frame_base_depth*3))),
        connectorframe.move(Location((0,0,-config.frame_base_depth*2))),
        wallbracket.move(Location((-config.frame_bracket_exterior_radius-config.minimum_structural_thickness*3,0,0))),
        reset_camera=Camera.KEEP
        )
