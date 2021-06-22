import logging
import sys

import hydra
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
from wasabi import msg

from pypefx._version import __version__
from pypefx.pipeline import Pipeline
from pypefx.shell import Shell
from pypefx.steps import PrintStep, ExportStep


def version() -> str:
    return f"pypefx {__version__}"


def goodbye() -> None:
    msg.good("Goodbye :)")


@hydra.main(config_path="..", config_name="..\\defaults")
def hydra_main(cfg: DictConfig) -> None:
    debug = HydraConfig.get().verbose

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(f"debug: {debug}")

    pipeline = Pipeline()

    mode = cfg.get("mode", None)
    logging.debug(f"mode: {mode}")
    if mode is None:
        msg.warn("pypefx mode is None -> exit")
        goodbye()
        return
    elif "cli" == mode:
        inp = cfg.get("input", None)
        logging.debug(f"inp: {inp}")

        out = cfg.get("output", None)
        logging.debug(f"output: {out}")

        profile = cfg.get("profile", None)
        logging.debug(f"profile: {profile}")

        if inp is not None and profile is not None:
            s = Shell(pipeline, cfg)
            s.do_load(profile)
            if out is not None and not any(isinstance(x, ExportStep) for x in s.pipeline.steps):
                s.pipeline.add_step(ExportStep(out))
            s.do_process(inp)
        goodbye()
        return
    elif "shell" == mode:
        s = Shell(pipeline=pipeline, cfg=cfg)
        s.cmdloop()
        goodbye()
        return
    elif "gui" == mode:
        # TODO
        msg.warn("not implemented yet")
        goodbye()
        return


def main():
    args = sys.argv[1:]
    if "--version" in args or "-v" in args:
        print(version())
        return

    hydra_main()
