# Printing Guide

![Fender-Bender Logo](assets/logo.svg){ align=right loading=lazy width=33%}

## Recommended Print Settings

Other than where noted, the standard Prusa Slicer "structural" profiles will be fine. Some components will require supports to print properly, and we strongly recommend using organic supports. You'll get best results from hand painting areas for support and using PETG supports for PLA parts or vice-versa (although that's not strictly required)

## The "Filament Bracket"

This bracket is the component responsible for ensuring that the filament smoothly moves through the system when feeding the extruder, and is redirected to the buffer when retracting.
The system requires one filament bracket for each filament you need to buffer (on the Prusa MMU3, you'll need 5 filament brackets).

### Bottom Bracket
This is the primary part of the filament bracket, supporting the PTFE tubes through the system. The filament bracket wheel mounts on top of this part.
Several alternative parts exist for different tube and connector configurations. The default part is for 3mm inner diameter / 6mm outer diameter PTFE tubing without a connector. See Resources for fittings and tubing for part sources


| Printing Requirements | &nbsp; |
| ----------------------- | ------ |
| Requires supports| :asterisk: This prints fine without supports but there are two small areas along the right and left sides (for the guide rail and for the lock clip) that may benefit from supports|
| Infill Requirements | :material-checkbox-multiple-blank-circle-outline: default Should be fine |

### Bracket Wheel
The wheel will mount on a bearing and sit on the bottom bracket. When the Filament Bracket is fully assembled, the wheel should spin freely.

| Printing Requirements | &nbsp; |
| ----------------------- | ------ |
| Requires supports| :material-checkbox-multiple-blank-circle-outline: no |
| Infill Requirements | :material-checkbox-multiple-blank-circle-outline: default Should be fine |


### Bracket Top
The bracket top slides into the bottom bracket and locks the wheel/bearing assembly into place.

| Printing Requirements | &nbsp; |
| ----------------------- | ------ |
| Requires supports| :asterisk: This prints fine without supports but there is a small area along the right side (for the lock clip) that may benefit from supports|
| Infill Requirements | :material-checkbox-multiple-blank-circle-outline: default Should be fine |

### Bracket Clip
If you've chosen a frame clip locking style, the bracket clips lock each filament bracket into place in the top frame to prevent it from coming out in the event of a printer jam.

| Printing Requirements | &nbsp; |
| ----------------------- | ------ |
| Requires supports| :material-checkbox-multiple-blank-circle-outline: no |
| Infill Requirements | :material-checkbox-multiple-blank-circle-outline: default Should be fine |

## Walls

The walls form the sides of each buffering chamber. A fully assembled filament bracket will have two complete wall assemblies.

### Guide Walls
The guide walls connect to the frame elements and hold the sidewalls in place

| Printing Requirements | &nbsp; |
| ----------------------- | ------ |
| Requires supports| :asterisk: This prints fine without supports but there are small divots on the top and bottom that may benefit from supports, but will be difficult to remove|
| Infill Requirements | :material-checkbox-multiple-blank-circle-outline: default Should be fine |

### Reinforced Side Walls
Reinforced sidewalls are for the exterior of a wall assembly and provide some extra rigidity to the assembled frame.

| Printing Requirements | &nbsp; |
| ----------------------- | ------ |
| Requires supports| :asterisk: This prints fine without supports but there are small divots on the sides that may benefit from supports, but will be difficult to remove|
| Infill Requirements | :material-checkbox-multiple-blank-circle-outline: default Should be fine |

### Side Walls
Side walls separate each filament chamber.

| Printing Requirements | &nbsp; |
| ----------------------- | ------ |
| Requires supports| :asterisk: This prints fine without supports but there are small divots on the sides that may benefit from supports, but will be difficult to remove|
| Infill Requirements | :material-checkbox-multiple-blank-circle-outline: default Should be fine |

## Frame

The frame holds everything together.

## Frame Top
This is one of the most critical components of the system. Each filament bracket should snap into the frame with a satisfying click when properly assembled. One of the wall assemblies will click into the bottom of the frame. In wall mounted installations, the frame top will also connect to the wall hanger.
The default part includes the cut for the wall hanger; if you prefer to print the self-standing version it will have a smoother exterior profile, but you'll have to choose alternative parts for the connector and bottom as well.

| Printing Requirements | &nbsp; |
| ----------------------- | ------ |
| Requires supports| :warning: This will require supports along the arch and the hanging bracket areas. Supports may be beneficial for the wall slots as well.|
| Infill Requirements | :asterisk: default Should be fine; but be aware that this part bears the weight of the assembled bracket and any stresses on it. If you've modified your defaults in a way that lessens the structural integrity of parts, you may want to modify to strengthen the part|

**Frame Connector**
This connects the two wall assemblies.
The default part includes a thicker wall to the wall side for wall mounted installations. The alternative "standing" file will provide a straight back line when coupled with the standing top and bottom components.

| Printing Requirements | &nbsp; |
| ----------------------- | ------ |
| Requires supports| :material-checkbox-multiple-blank-circle-outline: This will require supports along the arch and the hanging bracket areas. Supports may be beneficial for the wall slots as well.|
| Infill Requirements | :material-checkbox-multiple-blank-circle-outline: default Should be fine |

**Frame Bottom**
In hanging installations, this part is not strictly necessary. In hybrid or standing installations, this includes a flat bottom for a free-standing buffer.
The default part includes the stand but also has extra spacing for wall mounted installations. The "hanging-no-stand" alternative has a round bottom profile which uses less filament and a different appearance in hanging installations. The "standing" alternative eliminates the extra spacing for the wall hanging bracket, as well as the screw guide along the back.

| Printing Requirements | &nbsp; |
| ----------------------- | ------ |
| Requires supports| :warning: This will require supports along the arch. Supports may be beneficial for the wall slots as well.|
| Infill Requirements | :material-checkbox-multiple-blank-circle-outline: default Should be fine |