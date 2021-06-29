import argparse
import logging
import os
import sys
from enum import Enum
from pathlib import Path

from pypefx.commandrunner import CommandRunner

from pypefx.steps import ExportStep

from pypefx.shell import Shell

from pypefx.pipeline import Pipeline
from pypefx._version import __version__

from wasabi import msg
import youtube_dl


def version() -> str:
    return f"pypefx {__version__}"


def goodbye() -> None:
    msg.good("Goodbye :)")


# NOTE: ./defaults.ini : https://docs.python.org/3/library/configparser.html
# [pypefx]
# ; available modes: cli (default), shell, gui
# mode = cli
#
# mrs_watson_32_exe_path = plugins/tools/MrsWatson-0.9.8/Windows/mrswatson.exe
# mrs_watson_64_exe_path = plugins/tools/MrsWatson-0.9.8/Windows/mrswatson64.exe
# nano_host_32_exe_path = plugins/tools/Tone2 NanoHost v1.0.2/NanoHost32bit.exe
# nano_host_64_exe_path = plugins/tools/Tone2 NanoHost v1.0.2/NanoHost64bit.exe

class Mode(Enum):
    CLI = "cli"
    SHELL = "shell"
    GUI = "gui"


class YdlLogger(object):
    def debug(self, message):
        pass

    def warning(self, message):
        pass

    def error(self, message):
        msg.fail(message)


__temp_input_file = None


def ydl_hook(d):
    global __temp_input_file
    __temp_input_file = d["filename"]


def download_mp3(input: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "logger": YdlLogger(),
        "progress_hooks": [ydl_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([input])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        help="show version and exit",
        action="version",
        version=version(),
    )
    parser.add_argument("-d", "--debug", help="debug flag", action="store_true")
    parser.add_argument("-i", "--input", help="input file to process", type=str)
    parser.add_argument(
        "-u", "--url", help="flag, that the input is a url", action="store_true"
    )
    parser.add_argument("-o", "--output", help="output file to export", type=str)
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=[Mode.CLI.name, Mode.SHELL.name, Mode.GUI.name],
        help="increase output verbosity",
        default=Mode.CLI.name,
    )
    parser.add_argument(
        "-c",
        "--config",
        help="path to INI-config file",
        type=str,
        default="defaults.ini",
    )
    parser.add_argument(
        "-p", "--profile", help="path to profile.yaml to load", type=str, default=None
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(args.__dict__)

    p = Pipeline()
    s = Shell(p)

    input_file = None
    if args.url and args.input:
        download_mp3(args.input)
        global __temp_input_file
        logging.debug(f"TIF: {__temp_input_file}")
        input_file = __temp_input_file
        suffix = Path(input_file).suffix
        input_file = input_file.replace(suffix, ".mp3")
    elif args.input:
        input_file = args.input

    if args.profile:
        s.do_load(args.profile)

    output_file = None
    if args.output:
        output_file = args.output
        s.pipeline.add_step(ExportStep(output_file))

    if args.mode == Mode.CLI.name:
        if not args.profile:
            profile = s.ask_file_indexed("./projects", ".yaml")
            s.do_load(profile)
        logging.debug(f"MODE: CLI, INPUT: {input_file}")
        logging.debug(f"is input_file truthy?: {bool(input_file)}")

        if not input_file:
            msg.info("Choose Input File extension")
            ext = s.ask_indexed([".mp3", ".wav", ".flac"])
            input_file = s.ask_file_indexed(".", ext)

        if not output_file and not any(
                isinstance(x, ExportStep) for x in s.pipeline.steps
        ):
            output_file = s.ask_string("enter output file name")
            s.pipeline.add_step(ExportStep(output_file))

        s.do_process(input_file)
    elif args.mode == Mode.SHELL.name:
        s.cmdloop()
    elif args.mode == Mode.GUI.name:
        msg.fail("Gui not Implemented yet")
