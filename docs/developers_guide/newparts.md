# Creating new Fender-Bender parts

## Start with the Configuration

Except for the simplest of parts such as an M4 Bolt cut, each part should have it's own Class, descended from Partomatic, and a corresponding configuration. The Lock Pin is an example of a fairly simple part that exists within Fender-Bender. It's recommended as a simple part to read through to understand how this works.

The configuration is defined in [lock_pin_config.py](https://github.com/x0pherl/fender-bender/blob/main/src/lock_pin_config.py), which looks like this at the time of writing:

```
@dataclass
class LockPinConfig:
    stl_folder: str = "NONE"
    pin_length: float = 100
    tolerance: float = 0.1
    height: float = 4
    tie_loop: bool = True
```

### Configuration naming convention

Following the rule of defining the configuration in a file with the same name as the partomatic file with the `_config` added before the `.py` extension makes each configuration and Partomatic component easy to manage.

### Update BenderConfig to generate the appropriate configuration

In many cases, all of the configuration needed to understand how to build a part for Fender-Bender already exists in BenderConfig. If not, you will need to add additional configuration items to the BenderConfig definition as well as your configuration files.

Once those elements are all appropriately represented in BenderConfig, it is easy to add a helper property to BenderConfig to generate the appropriate configuration for your object. Again, looking at the Lock Pin we can find the `lock_pin_config` defined in [bender_config.py](https://github.com/x0pherl/fender-bender/blob/main/src/bender_config.py)

```
@property
    def lock_pin_config(self) -> LockPinConfig:
        return LockPinConfig(
            stl_folder=self.stl_folder,
            pin_length=self.frame_exterior_width,
            tolerance=self.frame_lock_pin_tolerance,
            height=self.minimum_structural_thickness,
        )
```

## Create a class descending from Partomatic

Once you've defined the configuration, you'll need to define a class descending from Partomatic to handle generation. Once again, the lock pin part is a simple example to read through.
[lock_pin.py](https://github.com/x0pherl/fender-bender/blob/main/src/lock_pin.py)

In addition to defining the class, most parts contain an internal variable for the configuration as well as the Part.

```
class LockPin(Partomatic):
    """a partomatic of the lock pin"""

    _config = LockPinConfig()
    _lockpin: Part
```

### Create a `load_config` method

The Partomatic base class requires that you create a load_config method -- in Fender-Bender this is generally handled through a yaml string. It's a good idea to simply pass the loading of the configuration over to the configuration object created above.

### Create a `compile` method

`compile` is the function called to create the part. With the lockpin class, the _lockpin part is created by this function. Many Fender-Bender components also have alternate parts that are generated in this step; we'll cover that later on in this document.

### Create a `display` method

`display` should display the ojbect using the ocp_vscode viewer. It isn't strictly necessary when building a part, but it can be very helpful to generate any parts to see if the part is designed properly.

### Create a `export_stls` method

Fender-Bender generally handles this through the `stl_folder` element of BenderConfig; which can define a relative path. If this value is set to "NONE" then no file is saved. THis is shown below for the lockpin part:

```
if self._config.stl_folder == "NONE":
            return
        output_directory = Path(__file__).parent / self._config.stl_folder
        output_directory.mkdir(parents=True, exist_ok=True)
        export_stl(self._lockpin, str(output_directory / "lock-pin.stl"))
```

## Handling alternative parts

Fender-Bender uses an "opinionated but flexible" philosophy. There is one default part generated, but many alternates are provided for folks with different opinions. Obviously, the code complexity grows with each alternative part.

### define the part

Let's say we wanted to provide an alternate locpin part. We'd start by adding another private Part within the class:

```
class LockPin(Partomatic):
    """a partomatic of the lock pin"""

    _config = LockPinConfig()
    _lockpin: Part
    _alt_lockpin: Part # now we've got a 2nd part
```

### update the `compile` method

The `compile` method must now create the `alt_lockpin` part. We won't show that detailed example here. In some cases, Fender-Bender creates a separate private method for generating the part rather than including the entire code in the `compile` method. In other cases, both the primary and alternate parts are generated calling the same function with different arguments.

Either approach keeps the `compile` method shorter and more readable.

### update the `display` method (optional, but recommended)

The display method doesn't _have_ to display each alternate part, but in most cases, each part is arranged and displayed so that the parts can be verified visually.

### update `export_stls`

There's not much point in creating alternate parts if we don't save them to disk. _Only_ the default part should be added directly to the root of the `stls` folder. Alternative parts belong in the `alt` subdirectory.

Before trying to write to the folder, we should make sure it exists, adding this line to the code shown above:

```
        Path(output_directory / "alt").mkdir(parents=True, exist_ok=True)
```

Then, we can save the part. By convention, alternate parts share the same base file name with a description of what makes it different at the end. Let's imagine that our alternate lock pin design was a left-handed design; we might name the part `lock-pin-left-handed.stl`

```        export_stl(
            self.print_in_place_wheel,
            str(
                output_directory
                / "alt/lock-pin-left-handed.stl"
            ),
        )
