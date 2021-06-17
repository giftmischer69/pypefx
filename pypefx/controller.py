import hydra
import logging
import subprocess
import sys
from omegaconf import DictConfig, OmegaConf

from wasabi import msg

from pypefx.pipeline import Pipeline
from pypefx.payload import Payload
from pypefx.steps import (
    PrintStep,
    SoxBassStep,
    VstStep,
    ExportStep,
    SpleeterStep,
    SoxGainStep,
    SoxCombineType,
    SoxTempoStep,
    SoxSpeedStep,
    Vst32Step,
)

from tkinter import filedialog


def ask_audio_file_tkinter():
    file_name = filedialog.askopenfilename(
        filetypes=(("Audio files", "*.wav;*.mp3;*.flac"), ("All files", "*.*"))
    )
    return file_name


def ask_string(prompt):
    return input(f"{prompt}\n : ")


def ask_wav_file_name(prompt):
    name = ask_string(prompt)
    if not name.endswith(".wav"):
        name = name + ".wav"
    return name


@hydra.main(config_path="..", config_name="..\\config")
def main(cfg: DictConfig):
    debug = cfg["debug"]

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(f"debug: {debug}")
        
    if "input" not in cfg:
        input_file = ask_audio_file_tkinter()
    else:
        input_file = cfg["input"]

    if "output" not in cfg:
        output_file = ask_wav_file_name("enter .wav output file name")
    else:
        output_file = cfg[
            "output"
        ]  # TODO: cli arg, cli arg -> replace suffix with _screwed.wav

    pipeline = Pipeline()

    # pipeline.add_step(SoxBassStep(6))
    # pipeline.add_step(SoxGainStep(-3, True, True))
    pipeline.add_step(
        SpleeterStep(
            bass_steps=[SoxGainStep(9)],
            drum_steps=[SoxBassStep(9)],
            vocal_steps=[SoxGainStep(-3)],
            other_steps=[SoxGainStep(-3)],
            combine_type=SoxCombineType.MERGE,
        )
    )
    # pipeline.add_step(
    #     VstStep(
    #         "plugins\\effects\\ChowTape-Win64\\Win64\\CHOWTapeModel.dll",
    #         "plugins\\effects\\ChowTape-Win64\\CHOWTapeModel Sink_Gritty.fxp",
    #     )
    # )
    # pipeline.add_step(
    #     VstStep(
    #         "plugins\\effects\\ADF05_RoughRider_310\\RoughRider3.dll",
    #         "plugins\\effects\\ADF05_RoughRider_310\\RoughRider3 OG - 04 - Good One.fxp",
    #     )
    # )
    # pipeline.add_step(
    #     Vst32Step(
    #         "plugins\\effects\\OCD_DSP_Virtue\\OCD DSP Virtue.dll",
    #         "plugins\\effects\\OCD_DSP_Virtue\\Digi Limiter   .fxp"
    #     )
    # )

    # pipeline.add_step(SoxGainStep(0, False, True))
    pipeline.add_step(SoxSpeedStep(0.84))
    pipeline.add_step(ExportStep(output_file))

    payload = Payload(input_file)

    pipeline.process(payload)

    # out_file = pipeline.get_output()

    msg.good(f"Wrote output_file: {output_file}")
