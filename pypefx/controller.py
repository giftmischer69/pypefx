import logging
import sys

import hydra
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
from wasabi import msg

from pypefx._version import __version__
from pypefx.pipeline import Pipeline
from pypefx.shell import Shell
from pypefx.steps import PrintStep


def version() -> str:
    return f"pypefx {__version__}"


@hydra.main(config_path="..", config_name="..\\defaults")
def hydra_main(cfg: DictConfig) -> None:
    debug = HydraConfig.get().verbose

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(f"debug: {debug}")

    pipeline = Pipeline()

    # temp
    for i in range(5):
        pipeline.add_step(PrintStep())
    # temp end

    s = Shell(pipeline=pipeline, cfg=cfg)
    s.cmdloop()


def main():
    args = sys.argv[1:]
    if "--version" in args or "-v" in args:
        print(version())
        return

    hydra_main()
