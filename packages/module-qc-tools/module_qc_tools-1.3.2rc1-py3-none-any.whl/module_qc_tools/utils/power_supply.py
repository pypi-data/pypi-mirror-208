#!/usr/bin/env python3
from __future__ import annotations

import logging

from module_qc_tools.utils.hardware_control_base import hardware_control_base

log = logging.getLogger("measurement")


class power_supply(hardware_control_base):
    def __init__(self, config, name="power_supply", *args, **kwargs):
        self.on_cmd = ""
        self.off_cmd = ""
        self.set_cmd = ""
        self.getV_cmd = ""
        self.getI_cmd = ""
        self.n_try = 0
        self.success_code = 0
        super().__init__(config, name, *args, **kwargs)
        if "emulator" in self.on_cmd:
            log.info(f"[{name}] running power supply emulator!!")

    def on(self, v=None, i=None):
        cmd = f'{self.on_cmd.replace("{v}", str(v)).replace("{i}", str(i))}'

        return self.send_command(
            cmd,
            purpose=f"turn on power supply with {v}V, {i}A",
            pause=1,
            success_code=self.success_code,
        )

    def set(self, v=None, i=None):
        cmd = f'{self.set_cmd.replace("{v}", str(v)).replace("{i}", str(i))}'

        return self.send_command(
            cmd,
            purpose=f"set power supply to {v}V, {i}A",
            pause=1,
            success_code=self.success_code,
        )

    def off(self):
        return self.send_command(
            self.off_cmd,
            purpose="turn off power supply",
            extra_error_messages=[
                f"Run directory: `{self.run_dir}`"
                f"Off command: `{self.off_cmd}`"
                "Please manually turn off power supply!!"
            ],
            success_code=self.success_code,
        )

    def getV(self):
        return self.send_command_and_read(
            self.getV_cmd,
            purpose="read voltage",
            unit="V",
            max_nTry=self.n_try,
            success_code=self.success_code,
        )

    def getI(self):
        return self.send_command_and_read(
            self.getI_cmd,
            purpose="read current",
            unit="A",
            max_nTry=self.n_try,
            success_code=self.success_code,
        )
