import os
from cmd import Cmd
from os import listdir
from os.path import join, isfile
from pathlib import Path

import yaml
from omegaconf import DictConfig
from wasabi import msg

from pypefx._version import __version__
from pypefx.payload import Payload
from pypefx.pipeline import Pipeline
from pypefx.steps import ExportStep


def is_present(in_file):
    return not (in_file is None or in_file == "" or not Path(in_file).exists())


class Shell(Cmd):
    def __init__(self, pipeline: Pipeline, cfg: DictConfig):
        super().__init__()
        self.prompt = "fxsh> "
        self.cfg = cfg
        self.pipeline = pipeline

    def preloop(self) -> None:
        msg.good(f"Hello from pyepfx Version: {__version__}")
        self.do_help("")

    def do_q(self, line):
        """ Quits the Shell """
        msg.info("Goodbye")
        return True

    def do_quit(self, line):
        """ Quits the Shell """
        return self.do_q(line)

    def do_display_graph(self, line):
        """ Displays the current pipeline configuration """
        # TODO
        msg.info(f"Display pipeline: {self.pipeline.name}")
        for step in self.pipeline.steps:
            msg.info(f"\t{type(step).__name__}")

    def do_save(self, line):
        """ Saves the current pipeline to a file """
        if self.pipeline.name == "untitled":
            self.pipeline.name = self.ask_string("enter project name")

        self.pipeline.save()

    def do_load(self, project_name):
        """ Loads the pipeline from a file """
        project_path = os.path.join("./projects/", f"{project_name}.yaml")
        if Path(project_path).exists():
            with open(project_path, "r") as f:
                self.pipeline = yaml.load(f)

    def do_process(self, in_file):
        """ Processes a song through the pipeline """
        # if there is no export step, ask if user wants to export
        # https://stackoverflow.com/a/32705845
        if not any(isinstance(x, ExportStep) for x in self.pipeline.steps):
            if self.ask_bool("do you want to export the result?"):
                out_file = self.cfg.get("output", None)
                if not is_present(out_file):
                    out_file = self.ask_string("enter file name for output file")
                    if not out_file.endswith(".mp3") or out_file.endswith(".wav") or out_file.endswith(".flac"):
                        out_file += self.ask_indexed([".mp3", ".wav", ".flac"])

                self.pipeline.add_step(ExportStep(out_file))

        if not is_present(in_file):
            in_file = self.cfg.get("input", None)

        if not is_present(in_file):
            in_file = self.ask_file_indexed(".", ".mp3")

        payload = Payload(in_file)
        self.pipeline.process(payload)

    def do_add_step(self, line):
        """ Adds a processing step to the pipeline """
        # TODO
        pass

    def ask_string(self, prompt):
        return input(f"{prompt}\n : ")

    def ask_int(self, dialog: str):
        return int(input(f"{dialog}\n: "))

    def ask_bool(self, dialog: str):
        return "y" in input(f"{dialog} (y/N)\n: ").lower()

    def ask_file_indexed(self, initial_folder, ext):
        if not initial_folder:
            initial_folder = os.getcwd()

        only_files = [
            join(initial_folder, f)
            for f in listdir(initial_folder)
            if (isfile(join(initial_folder, f)) and f.lower().endswith(ext))
        ]
        return self.ask_indexed(only_files)

    def ask_indexed(self, options_list):
        for index, option in enumerate(options_list):
            print(f"({index})".ljust(5, " "), " ", option)
        choice = self.ask_int("enter option number (0-n)")
        return options_list[choice]
