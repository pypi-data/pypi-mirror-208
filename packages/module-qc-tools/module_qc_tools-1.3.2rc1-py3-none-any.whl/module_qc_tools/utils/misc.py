#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
from pathlib import Path

import jsonschema
from jsonschema import validate

from module_qc_tools import data

log = logging.getLogger("measurement")


def get_identifiers(config):
    identifiers = {}
    identifiers["ChipID"] = config["RD53B"]["Parameter"]["ChipId"]
    identifiers["Name"] = config["RD53B"]["Parameter"]["Name"]
    identifiers["Institution"] = ""
    identifiers["ModuleSN"] = ""
    return identifiers


def get_meta_data(config):
    return {
        "FirmwareVersion": "",
        "FirmwareIdentifier": "",
        "ChannelConfig": "",
        "SoftwareVersion": "",
        "ChipConfigs": config,
        "SoftwareType": "",
    }


class bcolors:
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    BADRED = "\033[91m"
    ENDC = "\033[0m"


def check_meas_config(input_data, path):
    info_schema_path = str(data / "schema/config.json")
    with Path(info_schema_path).open() as inFile:
        info_schema = json.load(inFile)
    try:
        validate(instance=input_data, schema=info_schema)
    except jsonschema.exceptions.ValidationError as err:
        log.error(
            bcolors.BADRED
            + "Input measurement config fails schema check with the following error:"
            + bcolors.ENDC
        )
        log.error(bcolors.BADRED + f"Input config: {path}" + bcolors.ENDC)
        log.error(bcolors.BADRED + f"Json Schema: {info_schema_path}" + bcolors.ENDC)
        log.error(err.message)
        raise RuntimeError() from None
