from build123d import (BuildPart, BuildSketch, Part,
                add, Location,
                loft, Axis, Box, Align, GridLocations, Plane,
                chamfer, Rectangle, Mode)

def wall_slot(width, height, depth) -> Part:
    with BuildPart() as slot:
        with BuildSketch() as sk_base:
            Rectangle(height,width)
        with BuildSketch(Plane.XY.offset(depth)):
            Rectangle(height,width+depth*2)
        loft()
    return slot.part
        
    
def wall_cut_template(length, width,height:float, bottom:bool=True, post_count=2, tolerance:float=0.2) -> Part:
    """returns a template for splitting a box along the y axis for hanging
    on a wall"""
    effective_tolerance = -tolerance/2 if bottom else tolerance/2
    cut_unit = length/4
    with BuildPart() as cut:
        Box(length, width, cut_unit+effective_tolerance, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(Location((cut_unit-effective_tolerance,0,cut_unit+effective_tolerance))) as lip:
            Box(cut_unit+effective_tolerance, width, cut_unit, align=(Align.MIN, Align.CENTER, Align.MIN))
            chamfer(lip.faces().sort_by(Axis.Z)[-1].edges().sort_by(Axis.X)[0], cut_unit/2)
        with BuildPart(Location((-length/2,0,cut_unit+effective_tolerance))) as back_edge:
            Box(cut_unit*2+effective_tolerance,width,height-cut_unit*2,align=(Align.MIN, Align.CENTER, Align.MIN))
            chamfer(back_edge.faces().sort_by(Axis.Z)[-1].edges().sort_by(Axis.X)[0], cut_unit)
        with BuildPart(back_edge.faces().sort_by(Axis.X)[-1]):
            with GridLocations(0,width/post_count,1,post_count):
                add(wall_slot(length+effective_tolerance*3, height-cut_unit*2, cut_unit+effective_tolerance))
    return cut.part

with BuildPart() as hanger:
    Box(9,80,40, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with BuildPart(mode=Mode.INTERSECT):
        add(wall_cut_template(9,80,40,bottom=True, post_count=3, tolerance=.2)),

with BuildPart() as hung:
    Box(9,80,40, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with BuildPart(mode=Mode.SUBTRACT):
        add(wall_cut_template(9,80,40,bottom=False, post_count=3,tolerance=.2)),

from ocp_vscode import show
show(
hanger.part,
hung.part.move(Location((0,0,0))),
)
