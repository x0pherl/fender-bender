# ptfe-fittings

ptfe-fittings builds a set of 3d-printable twist-lock connectors for joining PTFE tubes, and potentially stepping down tube sizes. This can be useful for multi-material systems such as the MMU3 and the ERCF.

For those looking to eliminate as much friction as possible from the filament path, maintaining a 6mm OD x 3mm ID tube means the filament having less contact with the sides, while providing a sturdy wall that is less likely to crease or collapse causing tension on the filament.

## Code

The source file, `build.py` is used to generate the .stl files -- the 3d models. The other python files represent the shapes that are generated. The various parameters and tolerances are all stored in the .ini files -- it's possible to generate new sized parts by modifying those and executing `python3 ./build.py`

## Resources for fittings and tubing

You'll need to purchase Tube Fittings, and potentially tubing. Here are some sources that I've found here in the states

| Description                             | Possible Source |
| -----------                             | --------------- |
| PC4-M10 Straight Pneumatic Tube Fitting (for 4mm OD tubing) | [BIQU via Amazon](https://www.amazon.com/gp/product/B01IB81IHG/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) |
| 1/8th threaded PC6-01 Through fitting (for 6mm OD tubing)| [Robot Digg](https://www.robotdigg.com/product/755/Through-fitting-PC4-M6,-PC4-01,-PC6-M6-or-PC6-01-for-PTFE-Tubing) (be sure to select PC6-01) and print the -1-8th fitting parts|
| PTFE Teflon tubing (3mm Inner Diameter(ID) X 6mm Outer Diameter (OD)) | [uxcell via Amazon](https://www.amazon.com/gp/product/B09158R6LD)

## Recommended Print Settings
layer height: .15mm or lower (lower layer heights reduce friction if the filament is rubbing against the funnel feed)

## Modifying the Source

The included source file relies on the build123d library. I recommend following the [build123d installation instructions](https://build123d.readthedocs.io/en/latest/installation.html).

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Inspiration

While this work is unique project, inspiration was heavily drawn
from the happy concidence of [jurassic73](https://www.printables.com/@jurassic73) posting his [Magnetic Twist Lock PTFE Connector](https://www.printables.com/model/873440-magnetic-twist-lock-ptfe-connector) design at around the same time as [madebyjwillis] (https://www.instagram.com/madebyjwillis/) posted [How to Make a Twist Snap Design](https://www.instagram.com/p/C36VVdTr1WA)

Both of these creators' work was incredibly helpful in coding this project.

## License

This project is licensed under the terms of the MIT license [MIT](https://choosealicense.com/licenses/mit/)
