#!/usr/bin/env python3
from __future__ import annotations

import logging
import os
import subprocess
import time
from pathlib import Path

log = logging.getLogger("measurement")


class hardware_control_base:
    def __init__(self, config, name="hardware_control_base"):
        self._wd = Path.cwd()
        self._name = name
        self.run_dir = None
        member_variables = [
            attr
            for attr in dir(self)
            if not callable(getattr(self, attr)) and not attr.startswith("_")
        ]
        for member in config:
            if member in member_variables:
                setattr(self, member, config[member])

        if self.run_dir == "emulator":
            self.run_dir = Path.cwd()
        else:
            self.run_dir = Path(self.run_dir)

    def send_command(
        self,
        cmd,
        purpose="send command",
        extra_error_messages=None,
        pause=0,
        success_code=0,
    ):
        extra_error_messages = extra_error_messages or []

        os.chdir(self._wd)
        os.chdir(self.run_dir)
        result = subprocess.run(cmd, shell=True, capture_output=True)
        log.debug(result.stdout.decode("utf-8"))
        os.chdir(self._wd)

        if result.returncode != success_code:
            for extra_error_message in extra_error_messages:
                log.info(f"[{self._name}] {extra_error_message}")
            msg = f"[{self._name}] fail to {purpose}!!"
            raise RuntimeError(msg)
        log.debug(f"[{self._name}] {purpose}")

        time.sleep(pause)

        return result.returncode

    def send_command_and_read(
        self,
        cmd,
        type=float,
        purpose="send command and read",
        unit="",
        extra_error_messages=None,
        max_nTry=0,
        success_code=0,
    ):
        extra_error_messages = extra_error_messages or []
        os.chdir(self._wd)
        os.chdir(self.run_dir)
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        os.chdir(self._wd)

        log.debug(result.stdout.decode())

        # A while loop to retry communications in case of timeout error.
        # The maximum number of tries is determined by the function argument max_nTry.
        nTry = 0
        while result.returncode != 0 and nTry < max_nTry:
            nTry += 1
            for extra_error_message in extra_error_messages:
                log.info(f"[{self._name}] {extra_error_message}")
            log.info(f"Try again. Send command and read attempt {nTry} time(s).")
            os.chdir(self._wd)
            os.chdir(self.run_dir)
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
            os.chdir(self._wd)
            log.debug(result.stdout.decode())

        if result.returncode != success_code:
            msg = f"[{self._name}] fail to {purpose}!!"
            raise RuntimeError(msg)
        value = type(result.stdout.decode())
        for _extra_error_message in extra_error_messages:
            log.info(f"[{self._name}] {purpose}: {value}{unit}")

        return value, result.returncode
