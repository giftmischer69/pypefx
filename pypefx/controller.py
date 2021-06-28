import argparse
import logging
import os
import sys
from enum import Enum
from pathlib import Path

from pypefx.steps import ExportStep

from pypefx.shell import Shell

from pypefx.pipeline import Pipeline
from wasabi import msg

from pypefx._version import __version__

import sox


def version() -> str:
    return f"pypefx {__version__}"


def goodbye() -> None:
    msg.good("Goodbye :)")


# TODO: https://docs.python.org/3/library/configparser.html
# TODO ./defaults.ini

class Mode(Enum):
    CLI = "cli"
    SHELL = "shell"
    GUI = "gui"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", help="show version and exit", action="version", version=version())
    parser.add_argument("-d", "--debug", help="debug flag", action="store_true")
    parser.add_argument("-i", "--input", help="input file to process", type=str)
    parser.add_argument("-o", "--output", help="output file to export", type=str)
    parser.add_argument("-m", "--mode", type=str, choices=[Mode.CLI.name, Mode.SHELL.name, Mode.GUI.name],
                        help="increase output verbosity", default=Mode.CLI.name)
    parser.add_argument("-c", "--config", help="path to INI-config file", type=str, default="defaults.ini")
    parser.add_argument("-p", "--profile", help="path to profile.yaml to load", type=str, default=None)
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(args.__dict__)

    p = Pipeline()
    s = Shell(p)
    if args.input:
        input_file = args.input
    else:
        msg.info("Choose Input File extension")
        ext = s.ask_indexed([".mp3", ".wav", ".flac"])
        input_file = s.ask_file_indexed(".", ext)

    if args.profile:
        s.do_load(args.profile)
    else:
        profile = s.ask_file_indexed("./projects", ".yaml")
        s.do_load(profile)

    if args.output:
        output_file = args.output
    else:
        output_file = s.ask_string("enter output file name")
        if not any(
                isinstance(x, ExportStep) for x in s.pipeline.steps
        ):
            s.pipeline.add_step(ExportStep(s.output_file))

    if args.mode == Mode.CLI.name:
        s.output_file = output_file
        s.do_process(input_file)
    elif args.mode == Mode.SHELL.name:
        s.cmdloop()
    elif args.mode == Mode.GUI.name:
        msg.fail("Gui not Implemented yet")
