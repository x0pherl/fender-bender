#Updating `build.py`

Fender-Bender parts are all generated from any available configuration files by executing `build.py`. New parts should be added to the build script to ensure they are re-generated when the build script is run.

If you've followed this guide, the changes required should be minimal. The BenderConfig object is loaded from each configuration file in the line:

`config = BenderConfig(conf_file)`

which means we can use the config variable to get the customized part configuration using the configuration generator we added to BenderConfig. This can be done in a single line as shown for the lockpin object.

`LockPin(config.lock_pin_config).partomate()`

We simply instantiate a new LockPin object, using the `lock_pin_config` helper function of `config`, and then use the `partomate()` function to compile and save the part.