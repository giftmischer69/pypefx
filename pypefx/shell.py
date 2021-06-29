import logging
import os
from cmd import Cmd
from glob import glob
from os import listdir
from os.path import join, isfile
from pathlib import Path
from typing import List

import yaml
from numpy.core.defchararray import isnumeric
from wasabi import msg

from pypefx._version import __version__
from pypefx.payload import Payload
from pypefx.pipeline import Pipeline
from pypefx.steps import (
    ExportStep,
    SoxTempoStep,
    SoxSpeedStep,
    SoxBassStep,
    SoxDitherStep,
    SoxGainStep,
    PrintStep,
    VstStep,
    Vst32Step,
    SoxCombineType,
    SpleeterStep,
    Step,
)


def is_present(in_file):
    return not (in_file is None or in_file == "" or not Path(in_file).exists())


class Shell(Cmd):
    def __init__(self, pipeline: Pipeline):
        super().__init__()
        self.prompt = "fxsh> "
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

    def do_display(self, line):
        """ Displays the current pipeline configuration """
        msg.info(f"Display pipeline: {self.pipeline.name}")
        for step in self.pipeline.steps:
            msg.info(f"\t{type(step).__name__}")
            if type(step) == SpleeterStep:
                for stp in step.vocal_steps:
                    msg.info(f"\t\tvocal_step: {type(stp).__name__}")
                for stp in step.bass_steps:
                    msg.info(f"\t\tbass_step: {type(stp).__name__}")
                for stp in step.other_steps:
                    msg.info(f"\t\tother_step: {type(stp).__name__}")
                for stp in step.drum_steps:
                    msg.info(f"\t\tdrum_step: {type(stp).__name__}")
                msg.info(f"\t\tcombine_type: {step.combine_type}")

    def do_save(self, line):
        """ Saves the current pipeline to a file """
        if self.pipeline.name == "untitled":
            self.pipeline.name = self.ask_string("enter project name")

        Path("./projects/").mkdir(exist_ok=True)
        file_path = os.path.join("./projects/", f"{self.pipeline.name}.yaml")
        logging.info(f"Saving pipeline: {self.pipeline.name}")
        with open(file_path, "w") as f:
            f.write(yaml.dump(self.pipeline))

    def do_load(self, line):
        """ Loads the pipeline from a file """
        if line is None or line == "" or line.strip() == "":
            project_path = self.ask_file_indexed("./projects/", ".yaml")
        else:
            if line.endswith(".yaml"):
                project_path = line
            else:
                project_path = os.path.join("./projects/", f"{line}.yaml")

        if Path(project_path).exists():
            with open(project_path, "r") as f:
                logging.debug(f"loading pipeline: {project_path}")
                self.pipeline = yaml.load(f, Loader=yaml.Loader)
                logging.debug(f"Pipeline: {self.pipeline.name}")
                logging.debug(yaml.dump(self.pipeline))
        else:
            msg.fail(f"Project Path does not exist! {project_path}")

    def do_process(self, in_file):
        """ Processes a song through the pipeline """
        # if there is no export step, ask if user wants to export
        # https://stackoverflow.com/a/32705845
        if not any(isinstance(x, ExportStep) for x in self.pipeline.steps):
            if self.ask_bool("do you want to export the result?"):
                out_file = self.ask_string(
                    "enter file name for output file (remember .wav or .mp3 extension)"
                )

                if (
                        not out_file.endswith(".mp3")
                        and not out_file.endswith(".wav")
                        and not out_file.endswith(".flac")
                ):
                    out_file += self.ask_indexed([".mp3", ".wav", ".flac"])

                self.pipeline.add_step(ExportStep(out_file))

        if not is_present(in_file):
            in_file = self.ask_file_indexed(".", ".mp3")

        payload = Payload(in_file)
        self.pipeline.process(payload)

    def do_add(self, line):
        """ Adds a processing step to the pipeline """
        step_choices = [
            SoxTempoStep,
            SoxSpeedStep,
            SoxBassStep,
            SoxDitherStep,
            SoxGainStep,
            PrintStep,
            VstStep,
            Vst32Step,
            SpleeterStep,
            ExportStep,
        ]
        step_class = self.ask_step_indexed(step_choices)
        step = None
        if step_class == SoxTempoStep:
            logging.debug("Chose: Chose: SoxTempoStep")
            factor = self.ask_float_with_default("enter tempo factor", 1.0)
            step = SoxTempoStep(factor)
        elif step_class == SoxSpeedStep:
            logging.debug("Chose: SoxSpeedStep")
            factor = self.ask_float_with_default("enter tempo factor", 1.0)
            step = SoxTempoStep(factor)
        elif step_class == SoxBassStep:
            logging.debug("Chose: SoxBassStep")
            gain_db = self.ask_float_with_default("enter bass gain db", 0)
            frequency = self.ask_float_with_default("enter bass frequency", 100)
            slope = self.ask_float_with_default("enter bass slope", 0.5)
            step = SoxBassStep(gain_db, frequency, slope)
        elif step_class == SoxDitherStep:
            logging.debug("Chose: SoxDitherStep")
            step = SoxDitherStep()
        elif step_class == SoxGainStep:
            logging.debug("Chose: SoxGainStep")
            gain_db = self.ask_float_with_default("enter gain db", 0)
            normalize = self.ask_bool("normalize audio?")
            limiter = self.ask_bool("use limiter?")
            step = SoxGainStep(gain_db, normalize, limiter)
        elif step_class == PrintStep:
            logging.debug("Chose: PrintStep")
            step = PrintStep()
        elif step_class == VstStep:
            logging.debug("Chose: VstStep")
            plugin_path = Path("./plugins/effects/64bit").absolute()
            dll = self.ask_file_recursive_indexed(plugin_path, ".dll")
            fxp = self.ask_file_recursive_indexed(plugin_path, ".fxp")
            step = VstStep(dll, fxp)
        elif step_class == Vst32Step:
            logging.debug("Chose: Vst32Step")
            plugin_path = Path("./plugins/effects/32bit").absolute()
            dll = self.ask_file_recursive_indexed(plugin_path, ".dll")
            fxp = self.ask_file_recursive_indexed(plugin_path, ".fxp")
            step = Vst32Step(dll, fxp)
        elif step_class == SpleeterStep:
            logging.debug("Chose: SpleeterStep")
            bass_steps = self.ask_steps_loop(
                "add processing steps for the bass part of the song"
            )
            drum_steps = self.ask_steps_loop(
                "add processing steps for the drums of the song"
            )
            vocal_steps = self.ask_steps_loop(
                "add processing steps for the vocals of the song"
            )
            other_steps = self.ask_steps_loop(
                "add processing steps for other parts of the song"
            )
            combine_types = [SoxCombineType.MERGE, SoxCombineType.MIX, SoxCombineType.CONCATENATE,
                             SoxCombineType.SEQUENCE]
            msg.info("Choose combine type: ")
            combine_type = self.ask_indexed(combine_types)
            # bass steps
            # drum steps
            # vocal steps
            # other steps
            # combine_type
            step = SpleeterStep(bass_steps, drum_steps, vocal_steps, other_steps, combine_type)
        elif step_class == ExportStep:
            logging.debug("Chose: ExportStep")
            out_file = self.ask_string("enter file name for output file")
            if (
                    not out_file.endswith(".mp3")
                    and not out_file.endswith(".wav")
                    and not out_file.endswith(".flac")
            ):
                out_file += self.ask_indexed([".mp3", ".wav", ".flac"])
            step = ExportStep(out_file)

        if step is not None:
            self.pipeline.add_step(step)
            return

        msg.error("Something went wrong")

    def do_remove(self, line):
        # TODO add feature: remove step
        pass

    # TODO add feature: memento pattern (with decorator) / undo / redo
    def do_undo(self, line):
        pass

    def do_redo(self, line):
        pass

    def ask_string(self, prompt):
        return input(f"{prompt}\n : ")

    def ask_int(self, dialog: str):
        return int(input(f"{dialog}\n: "))

    def ask_float_with_default(self, dialog: str, default: float):
        inp = input(f"{dialog} (default: {default})\n : ")
        if inp is None or inp == "" or inp.strip() == "":
            choice = default
        else:
            choice = float(inp)
        return choice

    def ask_bool(self, dialog: str):
        return "y" in input(f"{dialog} (y/N)\n: ").lower()

    def ask_file_indexed(self, initial_folder, ext):
        logging.debug(f"initial_folder: {initial_folder}")
        if not initial_folder:
            initial_folder = os.getcwd()

        only_files = [
            join(initial_folder, f)
            for f in listdir(initial_folder)
            if (isfile(join(initial_folder, f)) and f.lower().endswith(ext))
        ]
        logging.debug(f"FILES: {only_files}")
        return self.ask_indexed(only_files)

    def ask_file_recursive_indexed(self, initial_folder, ext):
        logging.debug(f"initial_folder: {initial_folder}")
        if not initial_folder:
            initial_folder = os.getcwd()

        only_files = [
            y
            for x in os.walk(initial_folder)
            for y in glob(os.path.join(x[0], f"*{ext}"))
        ]
        logging.debug(f"FILES: {only_files}")
        return self.ask_file_name_indexed(only_files)

    def ask_indexed(self, options_list):
        for index, option in enumerate(options_list):
            print(f"({index})".ljust(5, " "), " ", option)
        choice = self.ask_int("enter option number (0-n)")
        return options_list[choice]

    def ask_step_indexed(self, steps_list):
        for index, option in enumerate(steps_list):
            print(f"({index})".ljust(5, " "), " ", option.__name__)
        choice = self.ask_int("enter option number (0-n)")
        return steps_list[choice]

    def ask_file_name_indexed(self, steps_list):
        for index, option in enumerate(steps_list):
            print(f"({index})".ljust(5, " "), " ", Path(option).name)
        choice = self.ask_int("enter option number (0-n)")
        return steps_list[choice]

    def ask_steps_loop(self, prompt) -> List[Step]:
        step_choices = [
            SoxBassStep,
            SoxDitherStep,
            SoxGainStep,
            PrintStep,
            VstStep,
            Vst32Step,
            ExportStep,
        ]
        inp = ""
        steps = []
        msg.info(prompt)
        while "q" not in inp:
            for index, option in enumerate(step_choices):
                print(f"({index})".ljust(5, " "), " ", option.__name__)
            inp = input("Choose Step (0-n)! (q to quit choosing steps)\n: ")
            if isnumeric(inp):
                choice = step_choices[int(inp)]
                if choice == SoxBassStep:
                    logging.debug("Chose: SoxBassStep")
                    gain_db = self.ask_float_with_default("enter bass gain db", 0)
                    frequency = self.ask_float_with_default("enter bass frequency", 100)
                    slope = self.ask_float_with_default("enter bass slope", 0.5)
                    steps.append(SoxBassStep(gain_db, frequency, slope))
                elif choice == SoxDitherStep:
                    logging.debug("Chose: SoxDitherStep")
                    steps.append(SoxDitherStep())
                elif choice == SoxGainStep:
                    logging.debug("Chose: SoxGainStep")
                    gain_db = self.ask_float_with_default("enter gain db", 0)
                    normalize = self.ask_bool("normalize audio?")
                    limiter = self.ask_bool("use limiter?")
                    steps.append(SoxGainStep(gain_db, normalize, limiter))
                elif choice == PrintStep:
                    logging.debug("Chose: PrintStep")
                    steps.append(PrintStep())
                elif choice == VstStep:
                    logging.debug("Chose: VstStep")
                    plugin_path = Path("./plugins/effects/64bit").absolute()
                    dll = self.ask_file_recursive_indexed(plugin_path, ".dll")
                    fxp = self.ask_file_recursive_indexed(plugin_path, ".fxp")
                    steps.append(VstStep(dll, fxp))
                elif choice == Vst32Step:
                    logging.debug("Chose: Vst32Step")
                    plugin_path = Path("./plugins/effects/32bit").absolute()
                    dll = self.ask_file_recursive_indexed(plugin_path, ".dll")
                    fxp = self.ask_file_recursive_indexed(plugin_path, ".fxp")
                    steps.append(Vst32Step(dll, fxp))
                elif choice == ExportStep:
                    logging.debug("Chose: ExportStep")
                    out_file = self.ask_string("enter file name for output file")
                    if (
                            not out_file.endswith(".mp3")
                            and not out_file.endswith(".wav")
                            and not out_file.endswith(".flac")
                    ):
                        out_file += self.ask_indexed([".mp3", ".wav", ".flac"])
                    steps.append(ExportStep(out_file))

        return steps
