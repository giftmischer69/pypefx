import sox


class TransformerSingleton:
    # https://python-patterns.guide/gang-of-four/singleton/
    _instance = None

    def __init__(self):
        raise RuntimeError("Call instance() instead")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print("Creating new instance")
            cls._instance = sox.Transformer()  # cls.__new__(cls)
            cls._instance.set_globals(
                dither=True, guard=True, multithread=True, replay_gain=True, verbosity=0
            )

        return cls._instance
