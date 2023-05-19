from abc import *
 
class Router:
    def __init__(self, PCB, resolution = 0.005):
        self.pcb = PCB
        self.resolution = resolution
        
        wire_name_list = list(self.pcb.net_list.keys())
        self.net = {wire_name:(tuple(zip(self.pcb.net_list[wire_name].name, self.pcb.net_list[wire_name].pin_no))) for wire_name in wire_name_list}