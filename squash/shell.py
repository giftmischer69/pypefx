import shutil
from abc import abstractmethod
from cmd import Cmd
from os import listdir
from os.path import isfile, join
from pathlib import Path
from typing import Any
import os
import yaml
from wasabi import msg
from squash._version import __version__

from graphviz import Digraph


def version():
    msg.info(f"squash Version: {__version__}")


class Effect:
    def __init__(
            self,
            name: str = "default",
            dll: Path = None,
            fxp: Path = None,
    ):
        self.name = name
        self.fxp = fxp
        self.dll = dll


class Node:
    def __init__(self, name: str):
        self.name = name
        self.input_file = None

    def __repr__(self):
        return f"Node.__repr__: {self.name}"


class InputNode(Node):
    def __init__(self, name: str):
        super().__init__(name)
        self.input_volume: float = 100


class OutputNode(Node):
    def __init__(self, name: str):
        super().__init__(name)
        self.input_volume: float = 100


class ProcessingNode(Node):  # sox, ffmpeg, etc
    def __init__(self, name: str):
        super().__init__(name)


class FfmpegConvertNode(ProcessingNode):
    def __init__(self, name: str, ext: str):
        super().__init__(name)
        self.ext = ext


class EffectNode(Node):
    def __init__(
            self,
            name: str,
            effect: Effect,
            input_volume: float = 100,
            output_volume: float = 100,
    ):
        super().__init__(name)
        self.effect = effect
        self.input_volume = input_volume
        self.output_volume = output_volume


class SpleeterNode(Node):
    def __init__(self, name: str, project_name: str):
        super().__init__(name)
        self.project_name = project_name


class CombinerNode(Node):
    def __init__(self, name: str):
        super().__init__(name)


class SoxSlowNode(ProcessingNode):
    def __init__(self, name: str, slow_param: float = 0.84):
        super().__init__(name)
        self.slow_param = slow_param


class Rack:
    def __init__(self, project_name: str = "default"):
        self.project_name = project_name
        self.nodes = {
            "input": InputNode("input"),
            "to_wav": FfmpegConvertNode("to_wav", "wav"),
            "slow": SoxSlowNode("slow", 0.84),
            "spleeter": SpleeterNode("spleeter", project_name),
            "bass_proc": ProcessingNode("bass_proc"),
            "vocal_proc": ProcessingNode("vocal_proc"),
            "drum_proc": ProcessingNode("drum_proc"),
            "other_proc": ProcessingNode("other_proc"),
            "bass_fx_01": EffectNode("bass_fx_01", Effect("bass_fx_01")),
            "vocal_fx_01": EffectNode("vocal_fx_01", Effect("vocal_fx_01")),
            "drum_fx_01": EffectNode("drum_fx_01", Effect("drum_fx_01")),
            "other_fx_01": EffectNode("other_fx_01", Effect("other_fx_01")),
            "combiner": CombinerNode("Combiner"),
            "output_fx_01": EffectNode("output_fx_01", Effect("output_fx_01")),
            "output_chow_fx": EffectNode(
                "output_chow_fx",
                Effect(
                    "output_chow_fx",
                    Path("../plugins/effects/ChowTape-Win64/Win64/CHOWTapeModel.dll"),
                    Path(
                        "../plugins/effects/ChowTape-Win64/CHOWTapeModel Sink_Gritty.fxp"
                    ),
                ),
            ),
            "output_comp_fx": EffectNode(
                "output_comp_fx",
                Effect(
                    "output_comp_fx",
                    Path("../plugins/effects/ADF05_RoughRider_310/RoughRider3.dll"),
                    Path(
                        "../plugins/effects/ADF05_RoughRider_310/RoughRider3 OG - 04 - Good One.fxp"
                    ),
                ),
            ),
            "output": OutputNode("output"),
        }
        self.graph = {
            "input": ["to_wav", None],
            "to_wav": ["slow", None],
            "slow": ["spleeter", None],
            "spleeter": ["bass_proc", "vocal_proc", "drum_proc", "other_proc", None],
            "bass_proc": ["bass_fx_01", None],
            "vocal_proc": ["vocal_fx_01", None],
            "drum_proc": ["drum_fx_01", None],
            "other_proc": ["other_fx_01", None],
            "bass_fx_01": ["combiner", None],
            "vocal_fx_01": ["combiner", None],
            "drum_fx_01": ["combiner", None],
            "other_fx_01": ["combiner", None],
            "combiner": ["output_fx_01", None],
            "output_fx_01": ["output_chow_fx", None],
            "output_chow_fx": ["output_comp_fx", None],
            "output_comp_fx": ["output", None],
            "output": [None],
        }

    def display_graph(self, file_name):
        dot = Digraph()
        for node in self.graph.keys():
            dot.node(node, node)
            edges = self.graph.get(node)
            if None in edges:
                edges.remove(None)
            for edge in edges:
                dot.edge(node, edge)

        if file_name is None or file_name == "":
            file_name = "graph"
        dot.render(file_name)
        msg.info(f"rendered graph: {file_name}.pdf")

    def save(self):
        Path("./projects/").mkdir(parents=True, exist_ok=True)
        project_path = os.path.join(".\\projects", f"{self.project_name}.yaml")
        with open(project_path, "w") as f:
            f.write(yaml.dump(self))
            msg.info(f"saved {project_path}")

    def render(self, in_file, out_file):
        rendering_folder = Path("./temp_rendering/")
        rendering_folder.mkdir(parents=True, exist_ok=True)

        if in_file is None or in_file == "" or not Path(in_file).exists():
            msg.warn("The Input file cannot be opened.")
            return

        for node_str in self.graph.keys():
            node = self.nodes.get(node_str)
            audio_path = os.path.join("./temp_rendering/", f"{node_str}.wav")
            msg.info(f"rendering node: {node.name}")
            if isinstance(node, InputNode):
                edges = self.graph.get(node_str)
                if None in edges:
                    edges.remove(None)
                for edge_key in edges:
                    edge_node = self.nodes.get(edge_key)
                    edge_node.input_file = in_file
                    msg.info(f"node: {node.name} | edge: {edge_key}")
            elif isinstance(node, FfmpegConvertNode):
                # TODO

                edges = self.graph.get(node_str)
                if None in edges:
                    edges.remove(None)
                for edge_key in edges:
                    edge_node = self.nodes.get(edge_key)
                    edge_node.input_file = in_file

        msg.info(f"removing folder: {rendering_folder}")
        shutil.rmtree(rendering_folder)


class Shell(Cmd):
    def __init__(self, debug: bool):
        super().__init__()
        self.prompt = "sqsh> "
        self.debug = debug
        self.rack = Rack()

    def preloop(self) -> None:
        version()
        msg.info("welcome to sqsh!")
        self.do_help("")

    def do_q(self, line):
        msg.info("Goodbye")
        return True

    def do_quit(self, line):
        return self.do_q(line)

    def do_display_graph(self, line):
        self.rack.display_graph(line)

    def do_save(self, line):
        if self.rack.project_name == "default":
            self.rack.project_name = self.ask_string("enter project name")

        self.rack.save()

    def do_load(self, project_name):
        project_path = os.path.join("./projects/", f"{project_name}.yaml")
        if Path(project_path).exists():
            with open(project_path, "r") as f:
                self.rack = yaml.load(f)

    def do_render(self, in_file):
        out_file = f"{self.rack.project_name}_rendered.wav"

        if in_file is None or in_file == "" or not Path(in_file).exists():
            in_file = self.ask_file_indexed(".", ".mp3")

        self.rack.render(in_file, out_file)

    def ask_string(self, prompt):
        return input(f"{prompt}\n : ")

    def ask_file_indexed(self, initial_folder, ext):
        only_files = [
            join(initial_folder, f)
            for f in listdir(initial_folder)
            if (isfile(join(initial_folder, f)) and f.lower().endswith(ext))
        ]
        return self.ask_indexed(only_files)

    def ask_indexed(self, options_list):
        for index, option in enumerate(options_list):
            print(f"({index})".ljust(5, " "), " ", option)
        choice = self.ask_int("enter option number (0-n)")
        return options_list[choice]

    def ask_int(self, prompt):
        return int(self.ask_string(prompt))
