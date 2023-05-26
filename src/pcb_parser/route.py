from abc import *
from pcb_parser.geometry import Point
from typing import Union

class Router:
    def __init__(self, PCB, resolution = 0.005):
        self.resolution = resolution
        self.pcb = PCB
        self.pcb.initialize()
        self.pcb.update_resolution(resolution)
        self.put_components()
        
        wire_name_list = list(self.pcb.net_list.keys())
        self.net = {wire_name:(tuple(zip(self.pcb.net_list[wire_name].name, self.pcb.net_list[wire_name].pin_no))) for wire_name in wire_name_list}

    def put_components(self):
        for comp_name in self.pcb.components_dict.keys():
            comp = self.pcb.get_component(comp_name)

            # comp 좌표 -> Integer
            pix_x = int(round(comp.min_x / self.resolution, 0))
            pix_y = int(round(comp.min_y / self.resolution, 0))
            
            self.pcb.put_component(comp_name, pix_x, pix_y, inplace=True)

    def get_pin_position(self, comp_name:str, pin_num:Union[str, int]) -> Point:
        """
        - Desciption -
        특정 component의 Pin 번호 입력 시, 해당 핀의 위치를 반환해주는 메소드. 

        - Input -
        comp_name(str): Component 이름  
        pin_num(int): Component의 Pin 번호 
        
        - Output -
        Point(Point): 해당 핀의 Point 객체 
        
        """
        
        comp = self.pcb.get_component(comp_name)
        comp_center = comp.center
        pin_position = comp_center + comp.pin_dict[str(pin_num)].position
        return pin_position