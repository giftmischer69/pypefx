import logging
import os
import shutil
import subprocess
import sys
from glob import glob
from pathlib import Path

import matchering as mg

from dearpygui.core import *
from dearpygui.simple import *

import sox


# use linked list instead of static list
# InputNode -> one successor
# (Optional) EffectsNode -> one successor
# SpleeterNode -> four successors
# for each of the four successors -> (Optinal EffectsNode)
# for each of the four succesor effectsnodes -> combiner
# combiner -> optional output effects
# optional output effects -> output node
def run_checked(command):
    logging.debug(f"running command: {command}")
    proc = subprocess.run(
        command,  # stdout=subprocess.STDOUT, stderr=subprocess.DEVNULL
    )
    return_code = proc.returncode
    logging.debug(f"return_code: {return_code}")
    if return_code != 0:
        logging.error(str(proc.__dict__))
        raise Exception(proc.stdout)


def combine_with_sox(project_name):
    cbn = sox.Combiner()
    cbn.convert(samplerate=44100, n_channels=2)
    project_path = Path(f"./{project_name}").absolute()
    project_files = [
        y for x in os.walk(project_path) for y in glob(os.path.join(x[0], "*.wav"))
    ]
    logging.debug(f"building project {project_name}")
    # create the output file
    out_file_name = f"{project_name}_combined.wav"
    cbn.build(project_files, out_file_name, "merge")
    return out_file_name


def apply_db(file, db):
    out_file = file.replace(".wav", "_new_db.wav")
    if db >= 0:
        sox_db_cmd = f"sox {file} {out_file} gain +{db}"
    else:
        sox_db_cmd = f"sox {file} {out_file} gain {db}"
    # tfm = sox.Transformer()
    # tfm.gain(db)
    # tfm.build(file, out_file)
    run_checked(sox_db_cmd)
    os.remove(file)
    return out_file


def apply_chow_tape(in_file_name):
    chow_temp_file_name = "chow_temp.wav"
    apply_clip_cmd = f""""plugins\\tools\\MrsWatson-0.9.8\\Windows\\mrswatson64.exe" -p "plugins\\effects\\ChowTape-Win64\\Win64\\CHOWTapeModel.dll","plugins\\effects\\ChowTape-Win64\\CHOWTapeModel Sink_Gritty.fxp" -i "{in_file_name}" -o {chow_temp_file_name}"""
    run_checked(apply_clip_cmd)
    return chow_temp_file_name


def apply_compressor(in_file_name):
    temp_comp_file_name = "compressed_temp.wav"
    apply_comp_cmd = f""""plugins\\tools\\MrsWatson-0.9.8\\Windows\\mrswatson64.exe" -p "plugins\\effects\\ADF05_RoughRider_310\\RoughRider3.dll","plugins\\effects\\ADF05_RoughRider_310\\RoughRider3 OG - 04 - Good One.fxp" -i "{in_file_name}" -o {temp_comp_file_name}"""
    run_checked(apply_comp_cmd)
    return temp_comp_file_name


def appply_slow(input_file, speed):
    new_input_file = input_file.name.replace(" ", "_")
    shutil.copy(input_file, new_input_file)
    temp01_screw = "screwed_temp01.wav"
    temp02_screw = "screwed_temp02.wav"
    to_wav_cmd = f"ffmpeg -y -i {new_input_file} {temp01_screw}"
    run_checked(to_wav_cmd)
    apply_screw_cmd = f"sox {temp01_screw} {temp02_screw} speed 0.84 dither"  # 0.84 -> -3DB // gain -20 norm
    run_checked(apply_screw_cmd)
    return temp02_screw


def cleanup_split_folder(project_path):
    logging.debug(f"Removing folder: {project_path}")
    shutil.rmtree(project_path)


def apply_matchering_command(file_name):
    out_file_name = "mastered_temp.wav"
    # Sending all log messages to the default print function
    # Just delete the following line to work silently
    mg.log(print)

    mg.process(
        # The track you want to master
        target=file_name,
        # Some "wet" reference track
        reference="reference.wav",
        # Where and how to save your results
        results=[
            mg.pcm24(out_file_name),
        ],
    )
    return out_file_name


def apply_sox_normalize(file_name):
    out_file = file_name.replace(".wav", "_sox_normalized.wav")
    tfm = sox.Transformer()
    tfm.gain(
        0,
        # normalize=True,
        limiter=True,
    )
    tfm.build(file_name, out_file)
    os.remove(file_name)
    return out_file


def remove_files(file_names):
    for file_name in file_names:
        try:
            os.remove(file_name)
            logging.debug(f"removed file: {file_name}")
        except Exception:
            pass


def main():
    # https://www.programiz.com/python-programming/examples/positive-negative-zero
    # https://linux.die.net/man/1/sox
    logging.basicConfig(level=logging.DEBUG)
    args = sys.argv[1:]
    print("Usage: python squash.py [project name] [input file]")
    project_name = Path(args[0])
    input_file = Path(args[1])

    slowed_file = appply_slow(input_file, 0.84)
    spleeter_cmd = (
        f"spleeter separate -o {project_name} -p spleeter:4stems {slowed_file}"
    )
    run_checked(spleeter_cmd)

    project_path = Path(f"./{project_name}").absolute()
    project_files = [
        y for x in os.walk(project_path) for y in glob(os.path.join(x[0], "*.wav"))
    ]
    for file in project_files:
        if "vocals" in file:
            apply_db(file, -3)
        elif "drums" in file:
            apply_db(file, 6)
        elif "bass" in file:
            apply_db(file, 9)  # 9
        elif "other" in file:
            apply_db(file, 3)

    out_file_name = combine_with_sox(project_name)
    chow_file_name = apply_chow_tape(out_file_name)
    compressed_file_name = apply_compressor(chow_file_name)
    sox_normalized_file_name = apply_sox_normalize(compressed_file_name)
    # mastered_file_name = apply_matchering_command(compressed_file_name)
    out_file = f"{project_name}.wav"
    shutil.copy(sox_normalized_file_name, out_file)
    cleanup_split_folder(project_path)
    remove_files([slowed_file, out_file, chow_file_name, compressed_file_name, sox_normalized_file_name])
    logging.info(f"finished! wrote: {out_file}")


if __name__ == "__main__":
    main()
