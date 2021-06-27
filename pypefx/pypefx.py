import logging
import sys

import hydra
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
from wasabi import msg

from pypefx._version import __version__
# from pypefx.gui import Gui
from pypefx.pipeline import Pipeline
from pypefx.shell import Shell
from pypefx.steps import (
    PrintStep,
    ExportStep,
    SoxDitherStep,
    SoxSpeedStep,
    SoxGainStep,
    SoxBassStep,
    VstStep,
    SpleeterStep,
    SoxCombineType,
)


def version() -> str:
    return f"pypefx {__version__}"


def goodbye() -> None:
    msg.good("Goodbye :)")


def temp_debug_sound(pipeline):
    pipeline.add_step(SoxDitherStep())
    pipeline.add_step(SoxBassStep(6))
    pipeline.add_step(SoxGainStep(-3, True, True))
    # pipeline.add_step(
    #    SpleeterStep(
    #        bass_steps=[SoxGainStep(9)],
    #        drum_steps=[SoxBassStep(9)],
    #        vocal_steps=[SoxGainStep(-3)],
    #        other_steps=[SoxGainStep(-3)],
    #        combine_type=SoxCombineType.MERGE,
    #    )
    # )
    pipeline.add_step(
        VstStep(
            "plugins\\effects\\ChowTape-Win64\\Win64\\CHOWTapeModel.dll",
            "plugins\\effects\\ChowTape-Win64\\CHOWTapeModel Sink_Gritty.fxp",
        )
    )
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

    pipeline.add_step(SoxDitherStep())
    pipeline.add_step(ExportStep("debug_audio.wav"))
    return pipeline


@hydra.main(config_path="..", config_name="..\\defaults")
def hydra_main(cfg: DictConfig) -> None:
    debug = HydraConfig.get().verbose

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(f"debug: {debug}")

    pipeline = Pipeline()

    # TODO REMOVE (TEMP)
    pipeline = temp_debug_sound(pipeline)

    mode = cfg.get("mode", None)
    mode = "shell"
    logging.debug(f"mode: {mode}")
    if mode is None:
        msg.warn("pypefx mode is None -> exit")
        goodbye()
        return
    elif "cli" == mode:
        s = Shell(pipeline, cfg)

        inp = cfg.get("input", None)
        logging.debug(f"inp: {inp}")
        if inp is None:
            msg.info("Choose Input File extension")
            ext = s.ask_indexed([".mp3", ".wav", ".flac"])
            inp = s.ask_file_indexed(".", ext)

        out = cfg.get("output", None)
        logging.debug(f"output: {out}")
        if out is None:
            out = s.ask_string("enter output file name")
            if not any(
                    isinstance(x, ExportStep) for x in s.pipeline.steps
            ):
                s.pipeline.add_step(ExportStep(out))

        profile = cfg.get("profile", None)
        logging.debug(f"profile: {profile}")
        s.do_load(profile)

        s.do_process(inp)
        goodbye()
        return
    elif "shell" == mode:
        s = Shell(pipeline=pipeline, cfg=cfg)
        s.cmdloop()
        goodbye()
        return
    elif "gui" == mode:
        # g = Gui(pipeline=pipeline, cfg=cfg)
        # g.run()
        goodbye()
        return


def main():
    args = sys.argv[1:]
    if "--version" in args or "-v" in args:
        print(version())
        return

    hydra_main()
