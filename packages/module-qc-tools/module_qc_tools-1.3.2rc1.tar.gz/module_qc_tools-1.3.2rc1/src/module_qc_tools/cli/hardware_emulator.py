#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path

import numpy as np

from module_qc_tools import data

if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources

rng = np.random.default_rng(42)
log = logging.getLogger(__name__)

_MODULE_STATE_FILE = data / "emulator" / "module_state.json"
_MODULE_CONNECTIVITY_FILE = "configs/connectivity/20UPGXM1234567_Lx_dummy.json"


def initialize_module_state():
    with resources.as_file(data / "emulator/module_state_template.json") as path:
        shutil.copyfile(path, _MODULE_STATE_FILE)


def get_module_state():
    # Copy module state from template if not existing
    if not _MODULE_STATE_FILE.is_file():
        initialize_module_state()

    with _MODULE_STATE_FILE.open() as serialized:
        return json.load(serialized)


def update_module_state(state):
    with _MODULE_STATE_FILE.open("w") as serialized:
        json.dump(state, serialized, indent=4)


def update_Vmux(chip_state):
    """
    This function updates the Vmux voltage values to the corresponding channel.
    Currently emulates MonitorV = 1, 30, 33, 37, 34, 38, 36, 32, and
    MonitorI = 0, 28, 29, 30, 31, 63.
    For other MonitorV and MonitorI channels, return a random number between 0 and 2.
    One needs to write a new if statement for a new MonitorV or MonitorI.
    Note that all grounds are assumed to be perfect (0V). R_Imux is assumed to be 10kohm.
    Also updates the internal ADC based on MonitorV/I setting
    """
    if chip_state["MonitorV"] == 0:
        chip_state["Vmux"] = 0.0
    elif chip_state["MonitorV"] == 1:
        if chip_state["MonitorI"] == 0:
            chip_state["Vmux"] = chip_state["Iref"] * 10000.0
        elif chip_state["MonitorI"] == 28:
            chip_state["Vmux"] = chip_state["IinA"] * 10000.0 / 21000.0
        elif chip_state["MonitorI"] == 29:
            chip_state["Vmux"] = chip_state["IshuntA"] * 10000.0 / 26000.0
        elif chip_state["MonitorI"] == 30:
            chip_state["Vmux"] = chip_state["IinD"] * 10000.0 / 21000.0
        elif chip_state["MonitorI"] == 31:
            chip_state["Vmux"] = chip_state["IshuntD"] * 10000.0 / 26000.0
        elif chip_state["MonitorI"] == 9:
            # Typical Imux9 value for NTC pad current.
            chip_state["Vmux"] = 0.054
        elif (
            (chip_state["MonitorI"] <= 63 and chip_state["MonitorI"] >= 32)
            or (chip_state["MonitorI"] == 26)
            or (chip_state["MonitorI"] == 27)
        ):
            chip_state["Vmux"] = 0.0
        else:
            # If non of the above MonitorI settings are satisfied, return a random number between 0 and 2.
            chip_state["Vmux"] = 2 * rng.random()
    elif chip_state["MonitorV"] == 30:
        chip_state["Vmux"] = 0
    elif chip_state["MonitorV"] == 33:
        chip_state["Vmux"] = chip_state["VinA"] / 4.0
    elif chip_state["MonitorV"] == 37:
        chip_state["Vmux"] = chip_state["VinD"] / 4.0
    elif chip_state["MonitorV"] == 34:
        chip_state["Vmux"] = chip_state["VDDA"] / 2.0
    elif chip_state["MonitorV"] == 38:
        chip_state["Vmux"] = chip_state["VDDD"] / 2.0
    elif chip_state["MonitorV"] == 36:
        chip_state["Vmux"] = chip_state["Vofs"] / 4.0
    elif chip_state["MonitorV"] == 32:
        chip_state["Vmux"] = chip_state["VrefOVP"] / 3.33
    elif chip_state["MonitorV"] == 8:
        # When measuring voltage for VcalMed or VCalHigh, it's essentially computing a liner equation plus/minus
        # a random number. The random number is generated within (-0.005, 0.005). The seed is set global so it's
        # deterministic and reproducible.
        if chip_state["InjVcalRange"] == 1:
            chip_state["Vmux"] = chip_state["InjVcalMed"] / 4096 * 0.8 + 0.005 * (
                2 * rng.random() - 1
            )
        elif chip_state["InjVcalRange"] == 0:
            chip_state["Vmux"] = chip_state["InjVcalMed"] / 4096 * 0.4 + 0.005 * (
                2 * rng.random() - 1
            )
    elif chip_state["MonitorV"] == 7:
        if chip_state["InjVcalRange"] == 1:
            chip_state["Vmux"] = chip_state["InjVcalHigh"] / 4096 * 0.8 + 0.005 * (
                2 * rng.random() - 1
            )
        elif chip_state["InjVcalRange"] == 0:
            chip_state["Vmux"] = chip_state["InjVcalHigh"] / 4096 * 0.4 + 0.005 * (
                2 * rng.random() - 1
            )
    elif chip_state["MonitorV"] == 2:
        # Typical Vmux value for NTC pad voltage.
        chip_state["Vmux"] = 0.084
    elif chip_state["MonitorV"] == 63:
        chip_state["Vmux"] = 0.0
    else:
        # If non of the above MonitorV settings are satisfied, return a random number between 0 and 2.
        chip_state["Vmux"] = 2 * rng.random()

    if chip_state["MonitorV"] == 30:
        chip_state["MonitoringDataAdc"] = 0
    else:
        if chip_state.get("ADCcalOffset") and chip_state.get("ADCcalSlope"):
            chip_state["MonitoringDataAdc"] = round(
                (chip_state["Vmux"] - chip_state["ADCcalOffset"])
                / chip_state["ADCcalSlope"]
            )
        else:
            chip_state["MonitoringDataAdc"] = 0

    return chip_state


def scanConsole():
    """
    This function emulates the effect of running YARR scanConsole to configure chips
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--controller",
        default="configs/controller/specCfg-rd53b-16x1.json",
        help="Controller",
    )
    parser.add_argument(
        "-c",
        "--connectivity",
        default=_MODULE_CONNECTIVITY_FILE,
        help="Connectivity",
    )
    parser.add_argument("-s", "--scan", default=None, help="Scan config")
    parser.add_argument("-n", "--nThreads", type=int, help="Number of threads")
    parser.add_argument("-o", "--output", default="./", help="Output directory")
    parser.add_argument("--skip-reset", action="store_true", help="skip reset")
    args = parser.parse_args()

    module_state = get_module_state()

    with Path(args.connectivity).open() as path:
        spec_connectivity = json.load(path)

    nChips = len(spec_connectivity["chips"])

    for chip in range(nChips):
        config_path = spec_connectivity["chips"][chip]["config"]
        abs_path = args.connectivity.rsplit("/", 1)[0] + "/" + config_path
        with Path(abs_path).open() as path:
            spec = json.load(path)
        GlobalConfig = spec["RD53B"]["GlobalConfig"]
        Parameter = spec["RD53B"]["Parameter"]
        # VDDA/D should be trimmed to 1.2 after chip configuring
        module_state[f"Chip{chip+1}"]["VDDA"] = min(1.2, module_state["Vin"])
        module_state[f"Chip{chip+1}"]["VDDD"] = min(1.2, module_state["Vin"])
        # MonitorI and V set according to chip configs
        module_state[f"Chip{chip+1}"]["MonitorI"] = GlobalConfig.get("MonitorI", 0)
        module_state[f"Chip{chip+1}"]["MonitorV"] = GlobalConfig.get("MonitorV", 0)
        # set InjVcalMed, InjVcalHigh and InjVcalRange based on the chip configs
        module_state[f"Chip{chip+1}"]["InjVcalMed"] = GlobalConfig.get("InjVcalMed", 0)
        module_state[f"Chip{chip+1}"]["InjVcalHigh"] = GlobalConfig.get(
            "InjVcalHigh", 0
        )
        module_state[f"Chip{chip+1}"]["InjVcalRange"] = GlobalConfig.get(
            "InjVcalRange", 0
        )
        module_state[f"Chip{chip+1}"]["MonitoringDataAdc"] = GlobalConfig.get(
            "MonitoringDataAdc", 0
        )
        ADCcalPar = Parameter.get("ADCcalPar", [0, 0, 0])
        module_state[f"Chip{chip+1}"]["ADCcalOffset"] = ADCcalPar[0] * 0.001
        module_state[f"Chip{chip+1}"]["ADCcalSlope"] = ADCcalPar[1] * 0.001

        # Update Vmux
        module_state[f"Chip{chip+1}"] = update_Vmux(module_state[f"Chip{chip+1}"])

    update_module_state(module_state)

    # YARR returns 0 when scan is run
    if args.scan is not None:
        return 0
    return 1


def write_register():
    """
    This function emulates the effect of running YARR write-register
    Currently only emulates register MonitorI, MonitorV. One needs to add a new if statement for a new register name.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, help="Name")
    parser.add_argument("value", type=str, help="Value")
    parser.add_argument(
        "-r",
        "--controller",
        default="configs/controller/specCfg-rd53b-16x1.json",
        help="Controller",
    )
    parser.add_argument(
        "-c",
        "--connectivity",
        default=_MODULE_CONNECTIVITY_FILE,
        help="Connectivity",
    )
    parser.add_argument("-i", "--chipPosition", type=int, help="chip position")
    args = parser.parse_args()

    module_state = get_module_state()

    with Path(args.connectivity).open() as path:
        spec_connectivity = json.load(path)

    nChips = len(spec_connectivity["chips"])

    log.info(args.name, args.value)

    for chip in range(nChips):
        if args.chipPosition is not None and chip is not args.chipPosition:
            continue
        if args.name == "MonitorI":
            module_state[f"Chip{chip+1}"]["MonitorI"] = int(args.value)
        elif args.name == "MonitorV":
            module_state[f"Chip{chip+1}"]["MonitorV"] = int(args.value)
        elif args.name == "InjVcalMed":
            module_state[f"Chip{chip+1}"]["InjVcalMed"] = int(args.value)
        elif args.name == "InjVcalHigh":
            module_state[f"Chip{chip+1}"]["InjVcalHigh"] = int(args.value)
        elif args.name == "InjVcalRange":
            module_state[f"Chip{chip+1}"]["InjVcalRange"] = int(args.value)
        module_state[f"Chip{chip+1}"] = update_Vmux(module_state[f"Chip{chip+1}"])

    update_module_state(module_state)


def control_PS():
    """
    This function emulates the effect of powering the module
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--action", choices=["on", "off", "getV", "getI"], help="Action to PS"
    )
    parser.add_argument("-v", "--voltage", type=float, help="Set voltage")
    parser.add_argument("-i", "--current", type=float, help="Set current")
    args = parser.parse_args()

    if args.action == "off":
        # Turning off the power simply means module states go back to initial states. Thus copy the initial states from the template
        initialize_module_state()
        sys.exit(0)

    module_state = get_module_state()

    if args.action == "getV":
        # measure Vin
        v = module_state["Vin"]
        sys.stdout.write(f"{v}")
        sys.exit(0)

    if args.action == "getI":
        # measure Iin
        i = module_state["Iin"]
        sys.stdout.write(f"{i}")
        sys.exit(0)

    if args.action == "on":
        nChips = module_state["nChips"]

        # check if the module has already been powered on
        already_power = module_state["Vin"] > 0

        # Calculate Vin based on the prediction (slope and offset), as well as the voltage and the current set to the power supply
        module_state["Vin"] = min(
            0.348293 / nChips * args.current + 1, args.voltage, 2.0
        )
        # Calculate Iin from the calculated Vin
        module_state["Iin"] = (module_state["Vin"] - 1) * nChips / 0.348293
        # Assume temperature increases linearly with Iin
        module_state["temperature"] = 25.0 + module_state["Iin"] * 2.0
        for chip in range(nChips):  # loop over all the chips
            # VinA = VinD = Vin
            module_state[f"Chip{chip+1}"]["VinA"] = module_state["Vin"]
            module_state[f"Chip{chip+1}"]["VinD"] = module_state["Vin"]
            # Fun assumption: VDDA/D = 1.1 before configuring; otherwise stay the same values
            module_state[f"Chip{chip+1}"]["VDDA"] = min(
                1.1 if not already_power else module_state[f"Chip{chip+1}"]["VDDA"],
                module_state["Vin"],
            )
            module_state[f"Chip{chip+1}"]["VDDD"] = min(
                1.1 if not already_power else module_state[f"Chip{chip+1}"]["VDDD"],
                module_state["Vin"],
            )
            module_state[f"Chip{chip+1}"]["Vofs"] = min(
                1.0, module_state["Vin"]
            )  # VOFS = 1V
            module_state[f"Chip{chip+1}"]["VrefOVP"] = 2.0  # VrefOVP = 2V
            module_state[f"Chip{chip+1}"]["IinA"] = (
                module_state["Iin"] / nChips / 2
            )  # IinA = Iin/nChips/2
            module_state[f"Chip{chip+1}"]["IinD"] = (
                module_state["Iin"] / nChips / 2
            )  # IinD = Iin/nChips/2
            module_state[f"Chip{chip+1}"]["IcoreA"] = min(
                0.2, module_state["Iin"] / nChips / 2
            )  # ICoreA assumed to be 0.2A
            module_state[f"Chip{chip+1}"]["IcoreD"] = min(
                0.2, module_state["Iin"] / nChips / 2
            )  # ICoreD assumed to be 0.2A
            module_state[f"Chip{chip+1}"]["IshuntA"] = (
                module_state[f"Chip{chip+1}"]["IinA"]
                - module_state[f"Chip{chip+1}"]["IcoreA"]
            )  # IShunt = Iin - Icore
            module_state[f"Chip{chip+1}"]["IshuntD"] = (
                module_state[f"Chip{chip+1}"]["IinD"]
                - module_state[f"Chip{chip+1}"]["IcoreD"]
            )
            module_state[f"Chip{chip+1}"]["Iref"] = 4e-6  # Iref = 4 uA
            if not already_power:
                module_state[f"Chip{chip+1}"]["MonitorI"] = 0  # default minitorI = 0
            if not already_power:
                module_state[f"Chip{chip+1}"]["MonitorV"] = 0  # default minitorV = 0
            module_state[f"Chip{chip+1}"] = update_Vmux(
                module_state[f"Chip{chip+1}"]
            )  # update Vmux voltage

        update_module_state(module_state)


def measureV():
    """
    This function emulates the effect of multimeter (measuring the Vmux)
    """
    module_state = get_module_state()

    nChips = module_state["nChips"]

    v = 0
    for chip in range(nChips):
        v += module_state[f"Chip{chip+1}"]["Vmux"]
    sys.stdout.write(f"{v}")
    sys.exit(0)


def read_adc():
    """
    This function emulates the effect of ADC reading
    R_Imux is assumed to be 10kohm.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--controller",
        default=data / "emulator/configs/controller/specCfg-rd53b-16x1.json",
        help="Controller",
    )
    parser.add_argument(
        "-c",
        "--connectivity",
        default=data / "emulator" / _MODULE_CONNECTIVITY_FILE,
        help="Connectivity",
    )
    parser.add_argument("-i", "--chip_position", type=int, help="chip position")
    parser.add_argument(
        "-I",
        "--readCurrent",
        help="Read current instead of voltage",
        action="store_true",
    )
    parser.add_argument(
        "-R", "--rawCounts", help="Read raw ADC counts", action="store_true"
    )
    parser.add_argument("vmux", type=int, help="Vmux")
    args = parser.parse_args()

    module_state = get_module_state()

    nChips = module_state["nChips"]

    # Update Vmux settings first
    for chip in range(nChips):
        if args.chip_position is not None and chip is not args.chip_position:
            continue
        if args.readCurrent:
            module_state[f"Chip{chip+1}"]["MonitorV"] = 1
            module_state[f"Chip{chip+1}"]["MonitorI"] = int(args.vmux)
        else:
            module_state[f"Chip{chip+1}"]["MonitorV"] = int(args.vmux)
        module_state[f"Chip{chip+1}"] = update_Vmux(module_state[f"Chip{chip+1}"])

    # Then read ADC
    for chip in range(nChips):
        if args.chip_position is not None and chip is not args.chip_position:
            continue
        if args.rawCounts:
            v = module_state[f"Chip{chip+1}"]["MonitoringDataAdc"]
            u = ""
        elif args.readCurrent:
            v = (module_state[f"Chip{chip+1}"]["Vmux"] / 10000.0) / 1e-6
            u = "uA"
        else:
            v = module_state[f"Chip{chip+1}"]["Vmux"]
            u = "V"
        sys.stdout.write(f"{v} {u}")
    sys.exit(0)


def read_ringosc():
    """
    This function emulates the effect of ROSC reading
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, help="Name")
    parser.add_argument(
        "-r",
        "--controller",
        default=data / "emulator/configs/controller/specCfg-rd53b-16x1.json",
        help="Controller",
    )
    parser.add_argument(
        "-c",
        "--connectivity",
        default=data / "emulator" / _MODULE_CONNECTIVITY_FILE,
        help="Connectivity",
    )
    parser.add_argument("-i", "--chip_position", type=int, help="chip position")
    args = parser.parse_args()

    with Path(args.connectivity).open() as path:
        spec_connectivity = json.load(path)

    nChips = len(spec_connectivity["chips"])

    for chip in range(nChips):
        if args.chip_position is not None and chip is not args.chip_position:
            continue

        rosc_freq = "500 " * 42
        sys.stdout.write(rosc_freq)
    sys.exit(0)


def measureT():
    """
    This function emulates the effect of NTC (measure module temperature)
    """
    module_state = get_module_state()

    T = module_state["temperature"]
    sys.stdout.write(f"{T}")
    sys.exit(0)


def switchLPM():
    sys.exit(0)
