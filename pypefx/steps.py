import logging
import os
import random
import shutil
import string
from abc import abstractmethod, ABC
from enum import Enum
from glob import glob
from pathlib import Path
from time import sleep
from typing import List

import sox
from wasabi import msg

from pypefx.commandrunner import CommandRunner
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


class SoxSpeedStep(Step):
    def __init__(self, factor):
        self.factor = factor

    def process(self, p: Payload) -> Payload:
        logging.debug("SoxTempoStep process")
        tfm = sox.Transformer()
        tfm.speed(self.factor)
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


class SoxDitherStep(Step):
    def __init__(self):
        pass

    def process(self, p: Payload) -> Payload:
        temp_input_file = "temp_input.wav"
        temp_output_file = "temp_output.wav"

        # p.message to file
        sox.Transformer().build(
            output_filepath=temp_input_file,
            input_array=p.message,
            sample_rate_in=p.sample_rate,
        )

        # Bitrate? : -b 8
        apply_vst_cmd = f"sox {temp_input_file} -r 44100 -c 2 {temp_output_file} dither"
        CommandRunner.run_checked(apply_vst_cmd)

        # p.message = read new file to array
        p.message = sox.Transformer().build_array(input_filepath=temp_output_file)

        # remove temp files
        os.remove(temp_input_file)
        os.remove(temp_output_file)

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


class Vst32Step(Step):
    mrs_watson_32_path = "plugins\\tools\\MrsWatson-0.9.8\\Windows\\mrswatson.exe"

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
        apply_vst_cmd = f""""{self.mrs_watson_32_path}" -p "{self.dll_path}","{self.fxp_path}" -i "{temp_input_file}" -o {temp_output_file}"""
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
    # MIX_POWER = "mix-power"
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

    def process(self, p: Payload) -> Payload:
        temp_dir_name = "".join(random.choice(string.ascii_lowercase) for i in range(8))
        Path(temp_dir_name).mkdir()
        temp_file_name = f"{temp_dir_name}.wav"
        sox.Transformer().build(
            input_array=p.message,
            sample_rate_in=p.sample_rate,
            output_filepath=temp_file_name,
        )
        spleeter_command = (
            f"spleeter separate -o {temp_dir_name} -p spleeter:4stems {temp_file_name}"
        )
        CommandRunner.run_checked(spleeter_command)

        # TODO Further
        project_path = Path(temp_dir_name).absolute()
        project_files = [
            y for x in os.walk(project_path) for y in glob(os.path.join(x[0], "*.wav"))
        ]
        temp_vocal_payload = Payload()
        temp_drum_payload = Payload()
        temp_bass_payload = Payload()
        temp_other_payload = Payload()

        for (
            file
        ) in (
            project_files
        ):  # TODO Process split files File Based like @ "D:\genos.se\effectsrack\squash.py"
            logging.debug(f"processing split file: {file}")
            if "vocals" in file:
                temp_vocal_payload.message = sox.Transformer().build_array(
                    input_filepath=file
                )
                for step in self.vocal_steps:
                    logging.debug(f"doing step:{type(step)} for file {file}")
                    temp_vocal_payload = step.process(temp_vocal_payload)
            elif "drums" in file:
                temp_drum_payload.message = sox.Transformer().build_array(
                    input_filepath=file
                )
                for step in self.vocal_steps:
                    logging.debug(f"doing step:{type(step)} for file {file}")
                    temp_drum_payload = step.process(temp_drum_payload)
            elif "bass" in file:
                temp_bass_payload.message = sox.Transformer().build_array(
                    input_filepath=file
                )
                for step in self.vocal_steps:
                    logging.debug(f"doing step:{type(step)} for file {file}")
                    temp_bass_payload = step.process(temp_bass_payload)
            elif "other" in file:
                temp_other_payload.message = sox.Transformer().build_array(
                    input_filepath=file
                )
                for step in self.vocal_steps:
                    logging.debug(f"doing step:{type(step)} for file {file}")
                    temp_other_payload = step.process(temp_other_payload)

        temp_payloads = [
            temp_vocal_payload,
            temp_bass_payload,
            temp_drum_payload,
            temp_other_payload,
        ]
        temp_file_names = []
        for payload in temp_payloads:
            temp_name = (
                "".join(random.choice(string.ascii_lowercase) for i in range(8))
                + ".wav"
            )
            temp_file_names.append(temp_name)
            sox.Transformer().build(
                input_array=payload.message,
                sample_rate_in=payload.sample_rate,
                output_filepath=temp_name,
            )

        combined_file_name = (
            "combined_"
            + "".join(random.choice(string.ascii_lowercase) for i in range(8))
            + ".wav"
        )

        mix_mode = self.combine_type.name
        if "power" not in mix_mode:
            mix_mode = mix_mode.lower()
            logging.debug(mix_mode)

        try:
            sox.Combiner().build(
                input_filepath_list=temp_file_names,
                output_filepath=combined_file_name,
                combine_type=mix_mode,
            )

            p.message = sox.Transformer().build_array(input_filepath=combined_file_name)
        finally:
            shutil.rmtree(temp_dir_name)
            for file_name in temp_file_names:
                os.remove(file_name)

            os.remove(combined_file_name)
            os.remove(temp_file_name)

        return p


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
