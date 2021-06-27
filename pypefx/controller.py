import argparse
import sys
from pathlib import Path

from wasabi import msg

from pypefx._version import __version__

import sox

def version() -> str:
    return f"pypefx {__version__}"


def goodbye() -> None:
    msg.good("Goodbye :)")


def debug_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="debug flag", action="store_true")
    parser.add_argument("-i", "--input", help="increase output verbosity", required=True, type=str)

    args = parser.parse_args()

    msg.good("HELLO WORLD!")
    msg.info(args)


def main():
    args = sys.argv[1:]
    if "--version" in args or "-v" in args:
        print(version())
        return

    debug_main()
