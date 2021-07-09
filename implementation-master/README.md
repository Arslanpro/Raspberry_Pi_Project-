# Implementation

The file structure of this project is based on [this file structure with internal packages](https://realpython.com/python-application-layouts/#application-with-internal-packages).

`/bin` contains the executable files. They will import a call to a main function in the runner script.

`/data` contains important data, such as databases or program in/outputs.

`/docs` contains documentation for this project. It might be removed if we do not the [docs folder in Managemement](https://gitlab.utwente.nl/cs20-1/management/-/tree/master/docs) instead.

`/misc` contains some random stuff that needs reorganising. This is a temporary folder and will likely be removed.

`/tests` contains all unit tests of the project. The directories inside this package match the package and module names of the source files. Each test module is prepended with `test_` (e.g. `wake_up_bright.alarm_clock.snooze.py` would have test module `tests/alarm_clock/test_snooze.py`)

`/wake_up_bright` is the top level package containing all source files of this project. It may be renamed in the future (make sure to update all references accordingly).

