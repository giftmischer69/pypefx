import copy
import logging

from pypefx.pipeline import Pipeline


class Memento:
    states = []
    index = 0
    max_entries = 5

    @classmethod
    def undoable(cls, func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            cls.states.append(copy.deepcopy(args[0].pipeline))
            if cls.index < cls.max_entries:
                cls.index = len(cls.states) - 1
            if len(cls.states) > cls.max_entries:
                cls.states.pop(0)
            logging.debug(f"cls.states: {cls.states}")
            logging.debug(f"cls.index: {cls.index}")

        return wrapper

    @classmethod
    def undo(cls) -> Pipeline:
        if cls.index > 0:
            cls.index -= 1
            logging.debug(f"undo: index:{cls.index}, states:{cls.states}")
            return cls.states[cls.index]

    @classmethod
    def redo(cls) -> Pipeline:
        if cls.index < cls.max_entries - 1:
            cls.index += 1
            logging.debug(f"redo: index:{cls.index}, states:{cls.states}")
            return cls.states[cls.index]