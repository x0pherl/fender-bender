# The Partomatic philosophy behind Fender-Bender

Build123d is a powerful library, but it leaves the creation of final parts up to the developer. For a project like fender-bender, with many related and interlocking parts, this can make releasing a new version a project in and of itself.

[Partomatic](https://github.com/x0pherl/fender-bender/blob/main/src/partomatic.py) enables _parametric modeling_ and standardizes some `build automation` for a part.

## Parametric Modeling
Parametric 3D modeling is a method of creating 3D models where the geometry is defined by parameters, allowing for easy adjustment by simply changing the values of these parameters. This approach enables the creation of flexible and reusable designs that can be quickly adapted to different requirements.

## Build Automation

Build automation

## The elements of Partomatic

There are three elements of Partomatic.
- `BuildablePart`
- `PartomaticConfig`
- `Partomatic`

## BuildablePart

BuildablePart is a small wrapper around build123d's Part class that adds some useful additional data for generating parts in an automated context. These variables are members of the BuildablePart class:]
```
    part: Part = field(default_factory=Part)
    display_location: Location = field(default_factory=Location)
    stl_folder: str = getcwd()
    _file_name: str = "partomatic"
```

`part` is simply a build123d `Part` object
`display_location` defines a build123d `Location` in which to display the object (this is useful combining multiple `BuildablePart`s into a single Partomatic object, and will be covered below)
`stl_folder` defines the folder in which the part should be saved
`file_name` (there are getters and setters for the `_filename` variable) defines the base file name. Note that this base will likely be combined with prefixes and suffixes that describe the parametric configuration, so any extension that is passed will be automatically stripped off.

## PartomaticConfig

The first element of Partomatic is the PartomaticConfig class. Descending a class from PartomaticConfig allows you to define any parametric values for your design.

PartomaticConfig makes it easy to load parametric values from Python parameters passed on instantiation, or through a YAML file -- you can even nest PartomaticConfig object definitions in a single YAML file.

YAML was chosen because YAML files are easily human-readable without deep technical knowledge. As an example, imagine a simple model of a wheel with a cut in the center for a bearing. We'll define both the wheel and the bearing. A simple example of a YAML configuration for a wheel with a bearing axle might look like:

```
wheel:
    depth: 10
    radius: 30
    bearing:
        radius: 4
        spindle_radius: 1.5
```
Now we can define PartomaticConfig objects for both the Wheel and the Bearing as follows:

```
from partomatic import PartomaticConfig
from dataclasses import field

class BearingConfig(PartomaticConfig):
    yaml_tree: str = "wheel/bearing"
    radius: float = 10
    spindle_radius: float = 2

class WheelConfig(PartomaticConfig):
    yaml_tree = "wheel"
    depth: float = 2
    radius: float = 50
    bearing: BearingConfig = field(default_factory=BearingConfig)
```

You may have noted a few things that aren't obvious given the YAML section above. Let's take a deeper look at yaml_tree and the field definition for the bearing.

### yaml_tree

The value `yaml_tree` defines the tree of the configuration within a file that you would like to load. For our example, not that "wheel" is the root object of our yaml file because our first line reads `wheel:`.

Bearing is a sub element of that wheel object, because it is at the same indent level as `depth` and `radius`. Partomatic separates objects on the tree with the `/` character, so we define the bearing's `yaml_tree` as `wheel/bearing` so it could be loaded independently from the same file.

Note that the yaml tree of the sub object is not _required_ to follow this pattern. In our sample case it makes it easy to load a bearing object from the same file as the wheel if only the bearing is required for some python files within our project. `yaml_tree` can also be passed when initializing the BearingConfig object, so it could be overwritten if appropriate.

### field factory

Field factory functions are beyond the scope of this documentation, however the [*dataclass* documentation](https://docs.python.org/3/library/dataclasses.html#default-factory-functions) covers this thoroughly.

For PartomaticConfig, all you need to understand is that if you are nesting PartomaticConfig objects, you should follow this pattern when adding the sub-object to the base part:
`<object_name>: <ObjectClass> = field(default_factory=<ObjectClass>)`
Have a look again at the bearing field of the `WheelConfig` object for an example.

### Instantiating a PartomaticConfig descendant

Now that we've got the `WheelConfig` (and it's member class `BearingConfig`) defined we need to create an instance of `WheelConfig`. We can instantiate this in several ways:
- default configuration
- loading from a file
- loading from a yaml string
- defining parameters

#### Instantiating with default configuration

If you're happy with the default values for your wheel configuration (and its bearing), it couldn't be simpler to instantiate:
`wheel_config = WheelConfig()`

#### Instantiating by loading from a file

Loading from a yaml file can make it easy to build multiple parts with different configurations.

In our example, you might define multiple wheel parts to support different bearings sizes and add prefixes with the standard bearing names. Each of these configurations can be defined in a separate file, and we can use automation to process each of them.

Instantiating a Partomatic object from a yaml file is as simple as passing a filename to a valid yaml file as the only parameter:
`wheel_config = WheelConfig('~/wheel/config/base_wheel.yml')`


#### Instantiating with a yaml string

If you've loaded a yaml string out of another object or from an environment variable, you can pass the entire yaml string instead of a filename as shown in this example:
```
wheel_yaml = """
wheel:
    depth: 10
    radius: 30
    bearing:
        radius: 4
        spindle_radius: 1.5
"""
wheel_config = WheelConfig(wheel_yaml)
```

Remember that you can also load the object from anywhere in a `yaml_tree`; so if the `wheel` object is defined in a yaml tree for a parent object you could use that as follows:

```
car_yaml = """
car:
    <some car values>
    drivetrain:
        <some drivetrain values>
        wheel:
            depth: 10
            radius: 30
            bearing:
                radius: 4
                spindle_radius: 1.5
"""
wheel_config = WheelConfig(car_yaml, yaml_tree='car/drivetrain/wheel')
```

#### Instantiating with parameters passed

If you understand the correct parameters from elsewhere in your code, you could simply define each of those as kwargs and pass them to the definition as in this example:

```
bearing_config = BearingConfig(radius=20, spindle_radius=10)
wheel_config = WheelConfig(depth=5, radius=50, bearing=bearing_config)
```

### Other PartomaticConfig fields

The base PartomaticConfig object also declares the following fields:
```
    stl_folder: str = "NONE"
    file_prefix: str = ""
    file_suffix: str = ""
    create_folders_if_missing: bool = True
```

#### `stl_folder`
This defines the folder in which Partomatic STL files will be generated

#### `file_prefix`
Your `Partomatic` object will generate one or more parts, and it defines file names for each part. The `file_prefix` allows you to define a prefix that will be added to each file when saving. This makes it possible to generate parts from multiple configurations in the same folder.

In our example, where we are defining multiple wheel parts to support different bearings sizes, we might add prefixes with the standard bearing names.

#### `file_suffix`
This works the same way as `file_prefix` (described above), but adds this string to the end of each generated file.

#### `create_folders_if_missing`
By default, Partomatic will create folders if they don't exist when exporting stl files. If you prefer it to only save parts if the folders already exist, you set this to `False`

## Partomatic

Partomatic is an [abstract base class](https://docs.python.org/3/library/abc.html) for components within a larger project.

Partomatic automatically handles the `__init__` method as well as `load_config`. Overriding these methods is not recommended.

### Defined Partomatic Variables

Partomatic defines two important variables that you descendent classes will inherit:
```
    _config: PartomaticConfig
    parts: list[BuildablePart] = field(default_factory=list)
```

`_config` stores the parameters from a PartomaticConfig object. `parts` is a list of BuildableParts, which partomatic will display or export when the appropriate methods are called.

### Abstract `compile` method

Partomatic defines an abstract methods which must be defined within a descendent class.

This method is responsible for generating the 3d geometry for each component. It should clear the parts list and regenerate each element of your design as a BuildablePart.

A simple example might look like this:

```
# ... Partomatic descendant class fragment

    def complete_wheel() -> Part:
        # <CODE TO GENERATE PART>

    def compile(self):
        """
        Builds the relevant parts for the filament wheel
        """
        self.parts.clear()
        self.parts.append(
            BuildablePart(
                self.complete_wheel(),
                "complete-wheel",
                stl_folder=self._config.stl_folder,
            )
        )

```

### Partomatic built-in methods

#### `display`

The `display` method will display each BuildablePart in the `parts` list in the appropriate display_location

#### `export_stls`

 This method calculates the appropriate file path based on the descendant class' `stl_folder`, `file_prefix`, the `BuildablePart`'s `file_name` and the `file_prefix`. If `create_folders_if_missing` is set to False, no part will be saved if the file is not present.

 #### `load_config`

 This method will load a configuration from file, kwargs, or a yaml string -- see the `PartomaticConfig` documentation for more details.

 #### `partomate`

 `partomate` is a convenience function that will execute the `compile` and `export_stls` functions of the Partomatic descendant.
