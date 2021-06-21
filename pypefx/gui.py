import logging

from pypefx.pipeline import Pipeline
from dearpygui.core import *
from dearpygui.simple import *

from pypefx.steps import PrintStep


class Gui:
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline

        for i in range(4):
            self.pipeline.add_step(PrintStep())

        self.input_volume = 100
        self.output_volume = 100
        self.setup()

    def setup(self):
        with window("Main"):
            set_primary_window("Main", True)
            with node_editor("Effects Rack"):
                with node("Input", x_pos=50, y_pos=100):
                    with node_attribute("Input Volume Attribute", output=True):
                        add_slider_float(
                            "Input Volume %",
                            width=150,
                            default_value=self.input_volume,
                            min_value=0,
                            max_value=100,
                            callback=lambda sender: self.set_input_volume(
                                get_value(sender)
                            ),
                        )
                set_item_width("Input", 150)

                with node("Output", x_pos=450, y_pos=100):
                    with node_attribute("Output Volume Attribute"):
                        add_slider_float(
                            "Output Volume %",
                            width=150,
                            default_value=self.output_volume,
                            min_value=0,
                            max_value=100,
                            callback=lambda sender: self.set_output_volume(
                                get_value(sender)
                            ),
                        )
                set_item_width("Output", 150)

        add_node_link(
            "Effects Rack", "Input Volume Attribute", "Output Volume Attribute"
        )

    def display(self):
        for i, step in enumerate(self.pipeline.steps):
            step_name = f"{type(step).__name__}_{i}"
            node_name = f"{step_name}_node"
            attr_name = f"{step_name}_attribute"
            out_attr_name = f"{step_name}_out_attribute"
            add_node(node_name, parent="Effects Rack", x_pos=150 * (i + 1), y_pos=200)
            add_node_attribute(attr_name, parent=node_name)
            end()
            add_node_attribute(out_attr_name, parent=node_name, output=True)
            end()
            end()

        start_dearpygui()

    def set_input_volume(self, volume: float):
        logging.debug(f"set input volume: {volume}")
        self.input_volume = volume

    def set_output_volume(self, volume: float):
        logging.debug(f"set output volume: {volume}")
        self.output_volume = volume
