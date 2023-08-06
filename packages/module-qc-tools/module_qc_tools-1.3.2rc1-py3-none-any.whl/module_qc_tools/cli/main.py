#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import sys

from module_qc_tools import data

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--prefix",
    action="store_true",
    default=False,
    help="display prefix",
)
args = parser.parse_args()


def main():
    if args.prefix:
        print(data)  # noqa: T201
        sys.exit(0)


if __name__ == "__main__":
    main()
