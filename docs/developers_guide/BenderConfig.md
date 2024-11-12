# The BenderConfig dataclass

The overall configuration for a fender-bender build is maintained in the BenderConfig dataclass, which is loaded in each of the `yaml` files in the [build-configs directory](https://github.com/x0pherl/fender-bender/tree/main/build-configs). Yaml was selected to keep the configuration files as human-readable as possible for non-developers.

## BenderConfig helper functions

Calculations regarding the configuration which need to be repeated in code should be implemented as @property helper functions within the BenderConfig object. As an example the connector frame needs to be deep enough to handle the tongue & groove connectors on both sides with some spacing in between.

Rather than calculating this in the code generating the part, BenderConfig has the following property definition (at the time of writing):

```
    @property
    def frame_connector_depth(self) -> float:
        """
        the depth of the connector frame
        """
        return self.frame_tongue_depth * 2 + self.minimum_thickness
```
This means when building assemblies for debugging or documentation purposes, the property can be called which insures that if future changes are made, that code will still function

## Other configuration generators

While a part generated for Fender-Bender is likely to have somewhat limited general purpose use, it makes sense to create idempotent parts that could be used within other contexts with their own free-standing configurations. To accomplish that, any part of even moderate complexity has it's own configuration dataclass.

However, it doesn't make sense to maintain multiple configuration files which need to be maintained and may contain some overlap. Instead, each object's configuration is derived from the overall BenderConfig dataclass.

BenderConfig has property definitions that allow other configuration types to be automatically generated for other part sets. For example, the top, bottom, and connector frames all use the FrameConfig dataclass, which can be generated from the BenderConfig as shown below:

```
bender_config = BenderConfig(config_path)
bottom_frame = BottomFrame(bender_config.frame_config)
```
