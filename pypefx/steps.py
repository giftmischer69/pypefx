import logging
import os
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from time import sleep
from typing import List

import sox
from wasabi import msg

from pypefx.command_runner import CommandRunner
from pypefx.payload import Payload


class Step(ABC):
    @abstractmethod
    def process(self, p: Payload) -> Payload:
        pass


class SoxTempoStep(Step):
    def __init__(self, factor):
        self.factor = factor

    def process(self, p: Payload) -> Payload:
        logging.debug("SoxTempoStep process")
        tfm = sox.Transformer()
        tfm.tempo(self.factor)
        p.message = tfm.build_array(input_array=p.message, sample_rate_in=p.sample_rate)
        return p


class SoxBassStep(Step):
    def __init__(self, gain_db: float, frequncy: float = 100.0, slope: float = 0.5):
        self.gain_db = gain_db
        self.frequency = frequncy
        self.slope = slope
        logging.debug(f"created: {self.__dict__}")

    def process(self, p: Payload) -> Payload:
        logging.debug("SoxBassStep process")
        tfm = sox.Transformer()
        tfm.bass(self.gain_db, self.frequency, self.slope)
        p.message = tfm.build_array(input_array=p.message, sample_rate_in=p.sample_rate)
        return p


class SoxGainStep(Step):
    def __init__(self, gain_db: float, normalize: bool = True, limiter: bool = False):
        self.limiter = limiter
        self.normalize = normalize
        self.gain_db = gain_db
        logging.debug(f"created: {type(self).__name__} : {self.__dict__}")

    def process(self, p: Payload) -> Payload:
        logging.debug("SoxBassStep process")
        tfm = sox.Transformer()
        tfm.gain(self.gain_db, self.normalize, self.limiter)
        p.message = tfm.build_array(input_array=p.message, sample_rate_in=p.sample_rate)
        return p


class PrintStep(Step):
    def process(self, p: Payload) -> Payload:
        msg.info(f"processing Payload, Payload size: {p.message.size}")
        sleep(1)
        return p


class VstStep(Step):
    mrs_watson_64_path = "plugins\\tools\\MrsWatson-0.9.8\\Windows\\mrswatson64.exe"

    def __init__(self, dll_path: str, fxp_path: str):
        self.fxp_path = fxp_path
        self.dll_path = dll_path

    def process(self, p: Payload) -> Payload:
        temp_input_file = "temp_input.wav"
        temp_output_file = "temp_output.wav"

        # p.message to file
        sox.Transformer().build(
            output_filepath=temp_input_file,
            input_array=p.message,
            sample_rate_in=p.sample_rate,
        )

        # apply vst to file
        apply_vst_cmd = f""""{self.mrs_watson_64_path}" -p "{self.dll_path}","{self.fxp_path}" -i "{temp_input_file}" -o {temp_output_file}"""
        CommandRunner.run_checked(apply_vst_cmd)

        # p.message = read new file to array
        p.message = sox.Transformer().build_array(input_filepath=temp_output_file)

        # remove temp files
        os.remove(temp_input_file)
        os.remove(temp_output_file)

        return p


class SoxCombineType(Enum):
    CONCATENATE = "concatenate"
    SEQUENCE = "sequence"
    MIX = "mix"
    MIX_POWER = "mix-power"
    MERGE = "merge"


class SpleeterStep(Step):
    def __init__(
        self,
        bass_steps: List[Step],
        drum_steps: List[Step],
        vocal_steps: List[Step],
        other_steps: List[Step],
        combine_type: SoxCombineType,
    ):
        self.combine_type = combine_type
        self.other_steps = other_steps
        self.vocal_steps = vocal_steps
        self.drum_steps = drum_steps
        self.bass_steps = bass_steps


class ExportStep(Step):
    def __init__(self, output_file: str):
        self.output_file = Path(f"./{output_file}").absolute().__str__()

    def process(self, p: Payload) -> Payload:
        msg.info(f"Exporting {self.output_file}")
        sox.Transformer().build(
            input_array=p.message,
            sample_rate_in=p.sample_rate,
            output_filepath=self.output_file,
        )
        return p
