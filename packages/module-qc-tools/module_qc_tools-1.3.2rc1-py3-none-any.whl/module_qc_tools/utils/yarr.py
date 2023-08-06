#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import json
import logging
import re
from pathlib import Path

from module_qc_tools.utils.hardware_control_base import hardware_control_base
from module_qc_tools.utils.misc import bcolors

# if sys.version_info >= (3, 9):
#    from importlib import resources
# else:
#    import importlib_resources as resources

log = logging.getLogger("measurement")


class yarr(hardware_control_base):
    def __init__(self, config, name="yarr", *args, **kwargs):
        self.controller = ""
        self.connectivity = ""
        self.scanConsole_exe = ""
        self.write_register_exe = ""
        self.read_register_exe = ""
        self.read_adc_exe = ""
        self.switchLPM_exe = ""
        self.lpm_digitalscan = ""
        self.read_ringosc_exe = ""
        self.success_code = 0
        self.emulator = False
        super().__init__(config, name, *args, **kwargs)
        if "emulator" in self.scanConsole_exe:
            self.emulator = True
            log.info(f"[{name}] running scanConsole emulator!!")
        if "emulator" in self.write_register_exe:
            self.emulator = True
            log.info(f"[{name}] running write_register emulator!!")
        if "emulator" in self.switchLPM_exe:
            self.emulator = True
            log.info(f"[{name}] running switchLPM emulator!!")
        connect_spec = self.get_connectivity()
        self._number_of_chips = len(connect_spec["chips"])
        self._disabled_chip_positions = set()
        for chip in range(self._number_of_chips):
            if not connect_spec["chips"][chip]["enable"]:
                self._disabled_chip_positions.add(chip)
        self._register = [{} for chip in range(self._number_of_chips)]

    def running_emulator(self):
        return self.emulator

    def configure(self, skip_reset=False):
        cmd = f'{self.scanConsole_exe} -r {self.controller} -c {self.connectivity} {"--skip-reset" if skip_reset else ""}'

        currLevel = log.getEffectiveLevel()
        log.setLevel(logging.DEBUG)
        # Below is the only case where success_code=1 is the default.
        # This is because the exit code of scanConsole for configuring the chip is 1 for success.
        # This will have to be removed once the YARR MR is merged (https://gitlab.cern.ch/YARR/YARR/-/issues/192).
        self.send_command(cmd, purpose="configure module", success_code=1)
        log.setLevel(currLevel)

        # Check for LP-mode
        for handler in log.handlers:
            if isinstance(handler, logging.FileHandler):
                filename = handler.baseFilename
                with Path(filename).open() as f:
                    for line in f:
                        if "LPM Status" in line:
                            match = int(re.search(r":\s*(\d+)$", line).group(1))
                            if match != 0:
                                log.warning(
                                    bcolors.WARNING
                                    + "Attention! Module is in low-power mode. If this is not intended, you can turn it off by running `./bin/switchLPM off` in YARR directory"
                                    + bcolors.ENDC
                                )

        return 0

    def run_scan(self, scan, output, skip_reset=False):
        cmd = f'{self.scanConsole_exe} -r {self.controller} -c {self.connectivity} -s {scan} -o {output} {"--skip-reset" if skip_reset else ""}'

        log.info(f"Running YARR scan: {scan} ...")
        # Always save scan output in log file
        currLevel = log.getEffectiveLevel()
        log.setLevel("DEBUG")
        self.send_command(cmd, purpose="configure module", success_code=0)
        log.setLevel(currLevel)

        return 0

    def write_register(self, name, value, chip_position=None):
        if chip_position in self._disabled_chip_positions:
            return 0
        if (
            chip_position is not None
            and self._register[chip_position].get(name) == value
        ):
            return 0
        cmd = f'{self.write_register_exe} -r {self.controller} -c {self.connectivity} {"-i "+str(chip_position) if chip_position is not None else ""} {name} {value}'
        self.send_command(cmd, purpose="write register", success_code=self.success_code)
        if chip_position is not None:
            self._register[chip_position][name] = value
        else:
            for chip in range(self._number_of_chips):
                self._register[chip][name] = value

        return 0

    def read_register(self, name, chip_position=None):
        if chip_position in self._disabled_chip_positions:
            return 0
        cmd = f'{self.read_register_exe} -r {self.controller} -c {self.connectivity} {"-i "+str(chip_position) if chip_position is not None else ""} {name}'
        return self.send_command_and_read(
            cmd, purpose="read register", success_code=self.success_code
        )

    def read_adc(self, vmux, chip_position=None, readCurrent=False, rawCounts=False):
        if chip_position in self._disabled_chip_positions:
            return 0
        cmd = f'{self.read_adc_exe} -r {self.controller} -c {self.connectivity} {"-i "+str(chip_position) if chip_position is not None else ""} {"-I " if readCurrent else ""} {"-R " if rawCounts else ""} {vmux}'
        return self.send_command_and_read(
            cmd, type=str, purpose="read adc", success_code=self.success_code
        )

    def read_ringosc(self, name, chip_position=None):
        if chip_position in self._disabled_chip_positions:
            return 0
        cmd = f'{self.read_ringosc_exe} -r {self.controller} -c {self.connectivity} {"-i "+str(chip_position) if chip_position is not None else ""} {name}'
        return self.send_command_and_read(cmd, type=str, purpose="read ringsoc")

    def set_mux(self, chip_position, v_mux=-1, i_mux=-1, reset_other_chips=True):
        for chip in range(self._number_of_chips):
            if chip == chip_position:
                # self.write_register(name="MonitorEnable", value=1, chip_position=str(chip))

                # Set Vmux=1 to measure the I_mux pad voltage when a non-negative I_mux value is passed.
                if i_mux >= 0:
                    v_mux = 1
                # Set Imux=63 when measuring NTC pad voltage through Vmux2.
                if v_mux == 2:
                    self.write_register(name="MonitorI", value=63, chip_position=chip)
                    self.write_register(
                        name="MonitorV", value=v_mux, chip_position=chip
                    )
                self.write_register(name="MonitorV", value=v_mux, chip_position=chip)
                if i_mux >= 0:
                    self.write_register(
                        name="MonitorI", value=i_mux, chip_position=chip
                    )
            elif reset_other_chips:
                self.write_register(name="MonitorV", value=63, chip_position=chip)

        return 0

    def reset_tempsens_enable(self, chip_position):
        self.write_register(
            name="MonSensSldoAnaEn", value=0, chip_position=chip_position
        )
        self.write_register(
            name="MonSensSldoDigEn", value=0, chip_position=chip_position
        )
        self.write_register(name="MonSensAcbEn", value=0, chip_position=chip_position)

        return 0

    def reset_tempsens_bias(self, chip_position):
        self.write_register(
            name="MonSensSldoAnaBias", value=0, chip_position=chip_position
        )

        self.write_register(
            name="MonSensSldoDigBias", value=0, chip_position=chip_position
        )

        self.write_register(name="MonSensAcbBias", value=0, chip_position=chip_position)

        return 0

    def reset_tempsens_dem(self, chip_position):
        self.write_register(
            name="MonSensSldoAnaDem", value=0, chip_position=chip_position
        )

        self.write_register(
            name="MonSensSldoDigDem", value=0, chip_position=chip_position
        )

        self.write_register(name="MonSensAcbDem", value=0, chip_position=chip_position)

        return 0

    def reset_tempsens(self, chip_position):
        self.reset_tempsens_enable(chip_position=chip_position)
        self.reset_tempsens_bias(chip_position=chip_position)
        self.reset_tempsens_dem(chip_position=chip_position)

        return 0

    def enable_tempsens(self, chip_position, v_mux=-1, reset_other_chips=True):
        # First reset all MOS sensors.
        self.reset_tempsens_enable(chip_position=chip_position)
        for chip in range(self._number_of_chips):
            if chip == chip_position:
                if v_mux == 14:
                    self.write_register(
                        name="MonSensSldoAnaEn", value=1, chip_position=chip
                    )
                elif v_mux == 16:
                    self.write_register(
                        name="MonSensSldoDigEn", value=1, chip_position=chip
                    )
                elif v_mux == 18:
                    self.write_register(
                        name="MonSensAcbEn", value=1, chip_position=chip
                    )
                else:
                    msg = "Incorrect VMUX value for measuring temperature!"
                    raise RuntimeError(msg)
            elif reset_other_chips:
                self.reset_tempsens_enable(chip_position=chip)

        return 0

    def set_tempsens_bias(
        self, chip_position, v_mux=-1, bias=0, reset_other_chips=True
    ):
        for chip in range(self._number_of_chips):
            if chip == chip_position:
                if v_mux == 14:
                    self.write_register(
                        name="MonSensSldoAnaSelBias", value=bias, chip_position=chip
                    )
                elif v_mux == 16:
                    self.write_register(
                        name="MonSensSldoDigSelBias", value=bias, chip_position=chip
                    )
                elif v_mux == 18:
                    self.write_register(
                        name="MonSensAcbSelBias", value=bias, chip_position=chip
                    )
                else:
                    msg = "Incorrect VMUX value for measuring temperature!"
                    raise RuntimeError(msg)
            elif reset_other_chips:
                self.reset_tempsens(chip_position=chip)

        return 0

    def set_tempsens_dem(self, chip_position, v_mux=-1, dem=0, reset_other_chips=True):
        for chip in range(self._number_of_chips):
            if chip == chip_position:
                if v_mux == 14:
                    self.write_register(
                        name="MonSensSldoAnaDem", value=dem, chip_position=chip
                    )
                elif v_mux == 16:
                    self.write_register(
                        name="MonSensSldoDigDem", value=dem, chip_position=chip
                    )
                elif v_mux == 18:
                    self.write_register(
                        name="MonSensAcbDem", value=dem, chip_position=chip
                    )
                else:
                    msg = "Incorrect VMUX value for measuring temperature!"
                    raise RuntimeError(msg)
            elif reset_other_chips:
                self.reset_tempsens(chip_position=chip)

        return 0

    def set_trim(self, chip_position, v_mux=-1, trim=0, reset_other_chips=True):
        for chip in range(self._number_of_chips):
            if chip == chip_position:
                if v_mux == 34:
                    self.write_register(
                        name="SldoTrimA", value=trim, chip_position=chip
                    )
                elif v_mux == 38:
                    self.write_register(
                        name="SldoTrimD", value=trim, chip_position=chip
                    )
                else:
                    msg = "Incorrect VMUX value for setting trim!"
                    raise RuntimeError(msg)
            elif reset_other_chips:
                self.write_register(name="SldoTrimA", value=0, chip_position=chip)
                self.write_register(name="SldoTrimD", value=0, chip_position=chip)

        return 0

    def switchLPM(self, position):
        cmd = f"{self.switchLPM_exe} {position}"
        return self.send_command(cmd, purpose="switch LP mode on/off")

    def get_connectivity(self):
        with Path(self.connectivity).open() as file:
            return json.load(file)

    def get_config(self, chip_position):
        connect_spec = self.get_connectivity()
        config_path = connect_spec["chips"][chip_position]["config"]
        path = self.connectivity.rsplit("/", 1)[0] + "/" + config_path

        with Path(path).open() as file:
            spec = json.load(file)

        with contextlib.suppress(KeyError):
            spec["RD53B"].pop("PixelConfig")

        return spec
