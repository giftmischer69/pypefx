from pathlib import Path
from typing import List
from dearpygui.core import *
from dearpygui.simple import *


class HouseWare:
    def __init__(
            self,
            name: str = "default",
            dll: Path = None,
            fxp: Path = None,
            input_volume: float = 100,
            output_volume: float = 100,
    ):
        self.output_volume = output_volume
        self.input_volume = input_volume
        self.name = name
        self.fxp = fxp
        self.dll = dll

class Controller:

    @classmethod
    def rack_set_input_effect_volume(cls, house_ware, param):
        pass


class Node:
    def __init__(self, house_ware: HouseWare):
        self.house_ware = house_ware

    def display(self, x: int, y: int):
        add_node(self.house_ware.name + " Node", parent="Cuisine Rack", x_pos=x, y_pos=y)
        end()

class OutputNode(Node):
    def __init__(self, house_ware: HouseWare):
        super().__init__(house_ware)
        self.output_degrees: float = 80



class InputNode(Node):
    def __init__(self, house_ware: HouseWare):
        super().__init__(house_ware)
        self.input_degrees: float = 100

    def display(self, x: int, y: int):
        add_node(self.house_ware.name + " Node", parent="Cuisine Rack", x_pos=150, y_pos=250)
        add_node_attribute(
            self.house_ware.name + " Input Volume Attribute", parent=self.house_ware.name + " Node"
        )
        add_slider_float(
            self.house_ware.name + " Input Volume %",
            width=150,
            default_value=self.input_degrees,
            min_value=0,
            max_value=100,
            parent=self.house_ware.name + " Input Volume Attribute",
            callback=lambda sender: Controller.rack_set_input_effect_volume(self.house_ware, get_value(sender)),
        )
        end()

class Cuisine:  # TODO display each incoming volume when previewing
    def __init__(self):
        self.dish_name: str = "default"
        self.input_degrees: float = 80
        self.output_degrees: float = 80
        self.effects: List[Node] = [Node(HouseWare())]

# https://relatedwords.io/kitchen
# https://github.com/hoffstadt/DearPyGui_06/wiki/Node-Editor
# 
def main():
    print("hello world")


if __name__ == '__main__':
    main()
