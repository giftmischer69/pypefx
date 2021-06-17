import logging
import os
import shutil
from pathlib import Path

import sox
from numpy.core._multiarray_umath import ndarray
from wasabi import msg

from pypefx.command_runner import CommandRunner


class Payload:
    def __init__(self, input_file: str = None):
        self.sample_rate = 44100
        if input_file:
            self.message: ndarray = self.get_wav_input_array(input_file)
        else:
            self.message = None

    def get_wav_input_array(self, input_file: str):
        msg.info(f"Preparing input_file: {input_file}")
        input_file_resolved = Path(input_file).absolute().__str__()
        input_file_replaced = Path(input_file.replace(" ", "_")).absolute().__str__()
        shutil.copy(input_file_resolved, input_file_replaced)
        final_input = input_file_replaced
        input_file_replaced_wav = None
        if not input_file_replaced.endswith(".wav"):
            suffix = Path(input_file_replaced).suffix
            logging.debug(f"SUFFIX:{suffix}")
            input_file_replaced_wav = input_file_replaced.replace(suffix, ".wav")
            ffmpeg_to_wav_cmd = f'ffmpeg -y -hide_banner -loglevel error -i "{input_file_replaced}" "{input_file_replaced_wav}"'
            CommandRunner.run_checked(ffmpeg_to_wav_cmd)
            final_input = input_file_replaced_wav

        message = sox.Transformer().build_array(input_filepath=final_input)
        os.remove(input_file_replaced)
        if input_file_replaced_wav:
            os.remove(input_file_replaced_wav)

        return message
