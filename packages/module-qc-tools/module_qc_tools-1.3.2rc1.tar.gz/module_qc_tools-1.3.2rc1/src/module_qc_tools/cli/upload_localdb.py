#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import requests

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="Walk through the specified directory (recursively) and attempt to submit all json files to LocalDB as the QC measurement"
)
parser.add_argument(
    "--path",
    default="Analysis/",
    help="Path to directory with output measurement files",
)
parser.add_argument(
    "--host",
    default="localhost",
    help="localDB server",
)
parser.add_argument(
    "--port",
    default=5000,
    help="localDB port",
)
parser.add_argument(
    "-n",
    "--dry-run",
    default=False,
    action="store_true",
    help="Dry-run, do not submit to localDB.",
)
parser.add_argument(
    "--out",
    default="tmp.json",
    help="Analysis output result json file path to save in the local host",
)
args = parser.parse_args()


def main():
    """
    Walk through the specified directory (recursively) and attempt to submit all json files to LocalDB as the QC measurement

    Args:
        path (str or pathlib.Path): root directory to walk through
        host (str): localDB server host
        port (int): localDB server port
        out  (str): analysis output result json file path to save in the local host

    Returns:
        None: The files are uploaded to localDB.
    """

    log.info("Searching candidate RAW json files...")
    flist = list(Path(args.path).rglob("*.json"))

    pack = []
    for path in flist:
        log.info(f"  - {path}")
        with path.open(encoding="utf-8") as fpointer:
            pack.extend(json.load(fpointer))

    log.info(f"Extracted {len(pack)} tests from {len(flist)} input files.")
    log.info("==> Submitting RAW results pack...")

    protocol = "http" if args.port != "443" else "https"

    if not args.dry_run:
        try:
            response = requests.post(
                f"{protocol}://{args.host}:{args.port}/localdb/qc_uploader_post",
                json=pack,
            )
            response.raise_for_status()

            data = response.json()

            log.info(data)

        except Exception as e:
            log.error("failure in uploading!")
            log.error(e)
            sys.exit(1)

        log.info(
            f"\nDone! LocalDB has accepted the following {len(data)} TestRun results"
        )
        for testRun in data:
            if testRun is None:
                log.info("A test run is already uploaded and will be skipped.")
                continue

            log.info(
                f'SerialNumber: {testRun["serialNumber"]}, Stage: {testRun["stage"]}, TestType: {testRun["testType"]}, QC-passed: {testRun["passed"]}'
            )

        try:
            with Path(args.out).open("w") as f:
                json.dump(data, f, indent=4)
                log.info(f"Saved the output TestRun to {args.out}")

        except Exception:
            log.warning(f"Failed to saved the output TestRun to {args.out}")
            altFilePath = f"/var/tmp/module-qc-tools-record-{int(time.time())}.json"

            try:
                with Path(altFilePath).open("w") as f:
                    json.dump(data, f, indent=4)
                log.info(f"Saved the output TestRun to {altFilePath}")

            except Exception:
                log.warning(f"Failed to saved the output TestRun to {altFilePath}")
                pass


if __name__ == "__main__":
    main()
