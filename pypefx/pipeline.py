import logging
from typing import List

from tqdm import tqdm

from pypefx.payload import Payload
from pypefx.steps import Step


class Pipeline:
    def __init__(self):
        self.steps: List[Step] = []
        self.result = None

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

    def get_output(self):
        return self.result
