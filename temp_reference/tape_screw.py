import atexit
import os
import shutil
import string
import subprocess
import sys
from pathlib import Path
import logging
import multiprocessing
import random

from tqdm import tqdm


class TempFileManager:
    def __init__(self):
        current_dir = os.getcwd()
        rand_str = "".join(random.choice(string.ascii_lowercase) for i in range(8))
        self.temp_folder = os.path.join(current_dir, ".temp_" + rand_str)
        if not os.path.exists(self.temp_folder):
            os.mkdir(self.temp_folder)
        atexit.register(self.clean_up)

    def get_temp_file(self, file_name):
        rand_str = "".join(random.choice(string.ascii_lowercase) for i in range(8))
        temp_file_path = os.path.join(
            self.temp_folder, file_name + "_" + rand_str + ".wav"
        )
        logging.debug(f"returning temp file name: {temp_file_path}")
        return temp_file_path

    def clean_up(self):
        logging.debug(f"removing: {self.temp_folder}")
        shutil.rmtree(self.temp_folder)


class ScrewApplier:
    def __init__(self):
        self.tfm = TempFileManager()

    def run_checked(self, command):
        proc = subprocess.run(
            command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )
        return_code = proc.returncode
        logging.debug(f"return_code: {return_code}")
        if return_code != 0:
            logging.error(str(proc.__dict__))
            raise Exception(proc.stdout)

    def apply_screw(self, input_path):

        input_path_replaced = input_path.__str__().replace(" ", "_")

        shutil.move(input_path, input_path_replaced)

        temp_wav = self.tfm.get_temp_file("temp")
        to_wav_cmd = f"ffmpeg -y -i {input_path_replaced} {temp_wav}"

        temp_norm = self.tfm.get_temp_file("norm")
        apply_norm_cmd = (
            f"sox {temp_wav} {temp_norm} gain -7 treble -2 bass +3 norm dither"
        )

        temp_comp = self.tfm.get_temp_file("comp")
        apply_comp_cmd = f""""plugins\\tools\\MrsWatson-0.9.8\\Windows\\mrswatson64.exe" -p "plugins\\effects\\ADF05_RoughRider_310\\RoughRider3.dll","plugins\\effects\\ADF05_RoughRider_310\\RoughRider3 OG - 04 - Good One.fxp" -i {temp_norm} -o {temp_comp}"""

        temp_clip = self.tfm.get_temp_file("clip")
        apply_clip_cmd = f""""plugins\\tools\\MrsWatson-0.9.8\\Windows\\mrswatson64.exe" -p "plugins\\effects\\ChowTape-Win64\\Win64\\CHOWTapeModel.dll","plugins\\effects\\ChowTape-Win64\\CHOWTapeModel Sink_Gritty.fxp" -i {temp_comp} -o {temp_clip}"""

        temp_screw = self.tfm.get_temp_file("screw")
        apply_screw_cmd = f"sox {temp_clip} {temp_screw} speed 0.84 dither"  # 0.84 -> -3DB // gain -20 norm

        out_file = self.screw_file_name(input_path_replaced)

        apply_comp2_cmd = f""""plugins\\tools\\MrsWatson-0.9.8\\Windows\\mrswatson64.exe" -p "plugins\\effects\\ADF05_RoughRider_310\\RoughRider3.dll","plugins\\effects\\ADF05_RoughRider_310\\RoughRider3 OG - 04 - Good One.fxp" -i {temp_screw} -o {out_file}"""

        commands = [
            to_wav_cmd,
            apply_norm_cmd,
            apply_comp_cmd,
            apply_clip_cmd,
            apply_screw_cmd,
            apply_comp2_cmd,
        ]

        for command in tqdm(commands):
            logging.debug(f"running command: {command}")
            self.run_checked(command)

        logging.info(f"finished! wrote: {out_file}")
        return True

    def screw_file_name(self, input_path):
        suffix = "." + input_path.__str__().split(".")[-1]
        screwed_path = input_path.__str__().replace(suffix, "_screwed.wav")
        return screwed_path


def usage():
    logging.warning(f"Usage: {sys.argv[0]} [input file(.mp3/.wav)/folder]")


if __name__ == "__main__":
    screw_applier = ScrewApplier()

    args = sys.argv[1:]

    if "--debug" in args:
        logging.basicConfig(level=logging.DEBUG)

    if not args[0] or "-h" in args or "--help" in args:
        usage()
        exit()

    path = Path(args[0]).absolute()

    if os.path.isfile(path):
        screw_applier.apply_screw(path)

    elif os.path.isdir(path):
        files = [os.path.join(path, x) for x in os.listdir(path)]

        agents = multiprocessing.cpu_count()
        with multiprocessing.Pool(processes=agents) as pool:
            result = pool.map(screw_applier.apply_screw, files)

    else:
        usage()
