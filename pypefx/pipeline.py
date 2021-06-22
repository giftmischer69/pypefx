import logging
import os
from pathlib import Path
from typing import List

from tqdm import tqdm

from pypefx.payload import Payload
from pypefx.steps import Step

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Pipeline:
    def __init__(self, name: str = None):
        self.steps: List[Step] = []
        self.result: Payload = Payload()
        self.name = name if name is not None else "untitled"

    def add_step(self, step: Step):
        self.steps.append(step)

    def process(self, payload: Payload):
        _payload = payload
        with tqdm(total=len(self.steps)) as bar:
            for index, step in enumerate(self.steps):
                logging.debug(f"running step: {index}, {type(step).__name__}")
                _payload = step.process(_payload)
                bar.update(1)
        self.result = _payload

    def save(self):
        Path("./projects/").mkdir(exist_ok=True)
        file_path = os.path.join("./projects/", f"{self.name}.yaml")
        logging.info(f"Saving pipeline: {self.name}")
        with open(file_path, "w") as f:
            f.write(dump(self))

    def save_steps(self):
        Path("./projects/").mkdir(exist_ok=True)
        file_path = os.path.join("./projects/", f"{self.name}_steps.yaml")
        logging.info(f"Saving pipeline steps: {self.name}")
        with open(file_path, "w") as f:
            f.write(dump(self.steps))

    def load_steps(self, project_name):
        file_path = os.path.join("./projects/", f"{project_name}_steps.yaml")
        logging.info(f"Loading pipeline steps with name: {project_name}")
        with open(file_path, "r") as f:
            self.name = project_name
            self.steps = load(f.read())
            self.result = Payload()
