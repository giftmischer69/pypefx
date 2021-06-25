from cx_Freeze import setup, Executable
from pypefx._version import __version__

requirements = [
    "wasabi",
    "dearpygui",
    "sox",
    "tqdm",
    "omegaconf",
    "pyyaml",
    "hydra-core"
]

options = {"build_exe": {"excludes": ["tkinter"],
                         "includes": [""]}}

executables = [
    Executable("./pypefx/__main__.py"),
]

setup(
    name="pypefx",
    version=__version__,
    description="apply an effects pipeline to a song.",
    executables=executables,
    options=options,
)
