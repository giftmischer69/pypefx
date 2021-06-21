import logging

from pypefx.pipeline import Pipeline
from dearpygui.core import *
from dearpygui.simple import *

from pypefx.steps import PrintStep


class Node:
    pass


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
            set_theme("Cherry")
            themes = [
                "Dark",
                "Light",
                "Classic",
                "Dark2",
                "Grey",
                "Dark Grey",
                "Cherry",
                "Purple",
                "Gold",
                "Red"
            ]
            with menu_bar("MenuBar", parent="Main"):
                with menu("Tools"):
                    add_menu_item("Render")  # TODO
                    add_menu_item("Save")  # TODO Save, ask file/project name if is default

                with menu("Add Effect Menu", label="Add Effect"):
                    add_input_text("Enter Effect Name", width=150)
                    # add_button("Add Effect", callback=self.rack_add_effect)
                    open_file_dialog(callback=lambda x: logging.info("select_directory_dialog" + x))

                with menu("Theme"):
                    for theme in themes:
                        add_menu_item(theme, callback=self.fx_set_theme, callback_data=theme)

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

                with node("Output", x_pos=750, y_pos=100):
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

    def display(self):
        last_out_attr = "Input Volume Attribute"
        for i, step in enumerate(self.pipeline.steps):
            step_name = f"{type(step).__name__}_{i}"
            node_name = f"{step_name}_node"
            attr_name = f"{step_name}_input_attribute"
            out_attr_name = f"{step_name}_out_attribute"
            add_node(node_name, parent="Effects Rack", x_pos=150 * (i + 1), y_pos=200)
            add_node_attribute(attr_name, parent=node_name)
            end()
            add_node_attribute(out_attr_name, parent=node_name, output=True)
            end()
            end()
            if last_out_attr != "":
                add_node_link("Effects Rack", attr_name, last_out_attr)
            last_out_attr = out_attr_name

        add_node_link("Effects Rack", last_out_attr, "Output Volume Attribute")
        start_dearpygui()

    def set_input_volume(self, volume: float):
        logging.debug(f"set input volume: {volume}")
        self.input_volume = volume

    def set_output_volume(self, volume: float):
        logging.debug(f"set output volume: {volume}")
        self.output_volume = volume

    def fx_set_theme(self, sender, data):
        log_info(f"setting theme: {sender}")
        set_theme(sender)
