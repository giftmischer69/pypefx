import logging

from dearpygui.core import *
from dearpygui.simple import *

from omegaconf import DictConfig

from pypefx.pipeline import Pipeline


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
            "Red"
        ]
        self.menu_bar_name = "Menu Bar"
        self.tools_menu_name = "Tools"
        self.add_effect_menu_name = "Add Effect Menu"
        self.add_effect_display_name = "Add Effect"
        self.theme_menu_name = "Theme"
        self.add_effect_button_name = "Add Effect Button"

        self.setup_main_window()
        self.setup_menu()
        self.setup_node_editor()

    def run(self):
        print("TEMP: running gui")
        start_dearpygui()
        pass

    def setup_menu(self):
        add_menu_bar(self.menu_bar_name, parent=self.main_window_name)
        add_menu(self.tools_menu_name)
        add_menu_item("Process")  # TODO like shell
        add_menu_item("Save")  # TODO like shell / Save, ask file/project name if is default
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
        end()

    def setup_node_editor(self):
        # TODO next
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
