from setuptools import find_packages, setup
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

setup(
    name="pypefx",
    version=__version__,
    packages=find_packages(include=["pypefx"]),
    entry_points={"console_scripts": ["pypefx = pypefx.pypefx:main"]},
    author='giftmischer69@protonmail.com',
    author_email='giftmischer69@protonmail.com',
    url='https://github.com/giftmischer69/pypefx',
    include_package_data=True,
    install_requires=requirements,
)
