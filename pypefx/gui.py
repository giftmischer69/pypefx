import logging
import random
import string

from dearpygui.core import *
from dearpygui.simple import *

from omegaconf import DictConfig

from pypefx.pipeline import Pipeline
from pypefx.steps import (
    Step,
    SoxTempoStep,
    SoxSpeedStep,
    SoxBassStep,
    SoxDitherStep,
    SoxGainStep,
    PrintStep,
    Vst32Step,
    VstStep,
    SoxCombineType,
    SpleeterStep,
    ExportStep,
)


class Node:
    def __init__(self, name: str = None):
        self.name = name
        if self.name is None:
            self.name = "".join(random.choice(string.ascii_lowercase) for i in range(8))
        self.input_attribute_name = self.name + "_input_attribute"
        self.output_attribute_name = self.name + "_output_attribute"

    def setup(self, x, y):
        add_node(self.name, x_pos=x, y_pos=y)
        add_node_attribute(self.input_attribute_name, output=True)
        end()
        add_node_attribute(self.output_attribute_name)
        end()
        end()


class StepNode(Node):
    def __init__(self, step: Step, index: int):
        self.name = f"{type(step).__name__}_{index}"
        self.step = step
        super().__init__(self.name)

    def setup(self, x, y):
        step_class = type(self.step)
        add_node(self.name, x_pos=x, y_pos=y)
        add_node_attribute(self.input_attribute_name, output=True)
        if step_class == SoxTempoStep:
            logging.debug("Chose: Chose: SoxTempoStep")
            add_slider_float(
                self.name + "_factor",
                min_value=0.1,
                max_value=2,
                default_value=self.step.factor,
                label="factor",
                no_input=True,  # TODO Temp
            )
        elif step_class == SoxSpeedStep:
            logging.debug("Chose: SoxSpeedStep")
            add_slider_float(
                self.name + "_factor",
                min_value=0.1,
                max_value=2,
                default_value=self.step.factor,
                width=150,
                label="factor",
                no_input=True,  # TODO Temp
            )
        elif step_class == SoxBassStep:
            logging.debug("Chose: SoxBassStep")
            add_slider_float(
                self.name + "_gain_db",
                min_value=-12,
                max_value=12,
                default_value=self.step.gain_db,
                width=150,
                label="gain_db",
                no_input=True,  # TODO Temp
            )
            add_slider_float(
                self.name + "_frequency",
                min_value=0,
                max_value=500,
                default_value=self.step.frequency,
                width=150,
                label="frequency",
                no_input=True,  # TODO Temp
            )
            add_slider_float(
                self.name + "_slope",
                min_value=0,
                max_value=1,
                default_value=self.step.slope,
                width=150,
                label="slope",
                no_input=True,  # TODO Temp
            )
        elif step_class == SoxDitherStep:
            logging.debug("Chose: SoxDitherStep")
        elif step_class == SoxGainStep:
            logging.debug("Chose: SoxGainStep")
            add_slider_float(
                self.name + "_gain_db",
                min_value=-12,
                max_value=12,
                default_value=self.step.gain_db,
                width=150,
                label="gain_db",
                no_input=True,  # TODO Temp
            )
            add_checkbox(
                self.name + "_normalize",
                default_value=self.step.normalize,
                label="normalize",
            )
            add_checkbox(
                self.name + "_limiter", default_value=self.step.limiter, label="limiter"
            )
        elif step_class == PrintStep:
            logging.debug("Chose: PrintStep")
        elif step_class == VstStep:
            logging.debug("Chose: VstStep")
            # TODO
        elif step_class == Vst32Step:
            logging.debug("Chose: Vst32Step")
            # TODO
        elif step_class == SoxCombineType:
            logging.debug("Chose: SoxCombineType")
            # TODO
        elif step_class == SpleeterStep:
            logging.debug("Chose: SpleeterStep")
            # TODO
        elif step_class == ExportStep:
            logging.debug("Chose: ExportStep")
            add_label_text(self.step.output_file)
            set_item_width(self.step.output_file, 10)

        end()
        add_node_attribute(self.output_attribute_name)
        end()
        end()


class InputNode(Node):
    def __init__(self, name: str = None):
        super().__init__(name)
        self.input_attribute_name = self.name + "_input_attribute"

    def setup(self, x, y):
        add_node(self.name, x_pos=x, y_pos=y)
        add_node_attribute(self.input_attribute_name, output=True)
        end()
        end()


class OutputNode(Node):
    def __init__(self, name: str = None):
        super().__init__(name)
        self.output_attribute_name = self.name + "_input_attribute"

    def setup(self, x, y):
        add_node(self.name, x_pos=x, y_pos=y)
        add_node_attribute(self.output_attribute_name)
        end()
        end()


class Gui:
    def __init__(self, pipeline: Pipeline, cfg: DictConfig):
        self.cfg = cfg
        self.pipeline = pipeline
        self.main_window_name = "Main"
        self.themes = [
            "Cherry",
            "Dark",
            "Light",
            "Classic",
            "Dark2",
            "Grey",
            "Dark Grey",
            "Purple",
            "Gold",
            "Red",
        ]
        self.menu_bar_name = "Menu Bar"
        self.tools_menu_name = "Tools"
        self.add_effect_menu_name = "Add Effect Menu"
        self.add_effect_display_name = "Add Effect"
        self.theme_menu_name = "Theme"
        self.add_effect_button_name = "Add Effect Button"
        self.node_editor_name = "Node Editor"

        self.nodes = self.get_nodes()

        self.setup_main_window()
        self.setup_menu()
        self.setup_node_editor()
        end()  # main_window end

    def run(self):
        print("TEMP: running gui")
        start_dearpygui()
        pass

    def setup_menu(self):
        add_menu_bar(self.menu_bar_name)
        add_menu(self.tools_menu_name)
        add_menu_item("Process")  # TODO like shell
        add_menu_item(
            "Save"
        )  # TODO like shell / Save, ask file/project name if is default
        add_menu_item("Load")  # TODO like shell
        end()
        add_menu(self.add_effect_menu_name, label=self.add_effect_display_name)
        add_input_text("Enter Effect Name", width=150)
        add_button(self.add_effect_button_name, label=self.add_effect_display_name)
        add_label_text("TODO ADD EFFECTS!")
        end()
        add_menu(self.theme_menu_name)
        for theme in self.themes:
            add_menu_item(theme, callback=self.fx_set_theme, callback_data=theme)
        end()
        end()

    def setup_node_editor(self):
        # TODO next
        add_node_editor(self.node_editor_name)
        last_node = None
        for index, _node in enumerate(self.nodes):
            x = 10 + 300 * index  # (index % 5)
            y = 100  # + (index // 5) * 150
            _node.setup(x, y)
            if last_node is not None:
                print(
                    f"add_node_link {last_node.input_attribute_name} {_node.output_attribute_name}"
                )
                add_node_link(
                    self.node_editor_name,
                    last_node.input_attribute_name,
                    _node.output_attribute_name,
                )
            if index != 0:
                last_node = _node
        add_node_link(
            self.node_editor_name,
            self.nodes[0].input_attribute_name,
            self.nodes[1].output_attribute_name,
        )
        end()
        pass

    def setup_main_window(self):
        add_window(self.main_window_name)
        set_primary_window(self.main_window_name, True)
        set_theme(self.themes[0])

    def set_input_volume(self, volume: float):
        logging.debug(f"set input volume: {volume}")
        # TODO self.input_volume = volume

    def set_output_volume(self, volume: float):
        logging.debug(f"set output volume: {volume}")
        # TODO self.output_volume = volume

    def fx_set_theme(self, sender, data):
        log_info(f"setting theme: {sender}")
        set_theme(sender)

    def get_nodes(self):
        nodes = [InputNode("Input Node")]
        for i, step in enumerate(self.pipeline.steps):
            nodes.append(StepNode(step, i))  # f"{type(step).__name__}_{i}"
        nodes.append(OutputNode("Output Node"))
        return nodes
