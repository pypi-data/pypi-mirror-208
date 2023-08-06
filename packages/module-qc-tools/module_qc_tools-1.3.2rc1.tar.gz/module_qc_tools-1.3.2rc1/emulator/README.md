# Toy emulator for module-qc-tool

The emulator uses `module_state.json` to store the current state of the module.
The initial state (when the module is powered off) is copied from the template
file `module_state_template.json`.

## `emulator-control-ps`

This command emulates the effect when turnning on/off or setting the power
supply.

```
$ emulator-control-ps --help
usage: control-PS [-h] [-a {on,off,getV,getI}] [-v VOLTAGE] [-i CURRENT]

optional arguments:
  -h, --help            show this help message and exit
  -a {on,off,getV,getI}, --action {on,off,getV,getI}
                        Action to PS
  -v VOLTAGE, --voltage VOLTAGE
                        Set voltage
  -i CURRENT, --current CURRENT
                        Set current
```

## `emulator-measureV`

This command emulates the Vmux measurement for the module, which should run as
follows:

```
emulator-measureV
```

## `emulator-measureT`

This command emulates the temperature measurement for the module, which should
run as follows:

```
emulator-measureT
```

## `emulator-scanConsole`

`emulator-scanConsole` emulates the effect when configuring a module.

```
$ emulator-scanConsole --help
usage: scanConsole [-h] [-r CONTROLLER] [-c CONNECTIVITY] [-n NTHREADS]
                   [--skip-reset]

optional arguments:
  -h, --help            show this help message and exit
  -r CONTROLLER, --controller CONTROLLER
                        Controller
  -c CONNECTIVITY, --connectivity CONNECTIVITY
                        Connectivity
  -n NTHREADS, --nThreads NTHREADS
                        Number of threads
  --skip-reset          skip reset
```

## `emulator-write-register`

`emulator-write-register` emulates the effect when writing a register for a
module.

```
$ emulator-write-register --help
usage: write-register [-h] [-r CONTROLLER] [-c CONNECTIVITY] [-i CHIPPOSITION]
                      [--skip-reset]
                      name value

positional arguments:
  name                  Name
  value                 Value

optional arguments:
  -h, --help            show this help message and exit
  -r CONTROLLER, --controller CONTROLLER
                        Controller
  -c CONNECTIVITY, --connectivity CONNECTIVITY
                        Connectivity
  -i CHIPPOSITION, --chipPosition CHIPPOSITION
                        chip position
```

## `emulator-switch-lpm`

`emulator-switch-lpm` emulates the effect when toggling low power mode

```

TBD
$ emulator-write-register --help
usage: write-register [-h] [-r CONTROLLER] [-c CONNECTIVITY] [-i CHIPPOSITION]
                      [--skip-reset]
                      name value

positional arguments:
  name                  Name
  value                 Value

optional arguments:
  -h, --help            show this help message and exit
  -r CONTROLLER, --controller CONTROLLER
                        Controller
  -c CONNECTIVITY, --connectivity CONNECTIVITY
                        Connectivity
  -i CHIPPOSITION, --chipPosition CHIPPOSITION
                        chip position
```
