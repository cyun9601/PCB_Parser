import json 
from pathlib import Path
from dataclasses import dataclass

class D_type:
    def __init__(self, **kwargs) -> None:
        self.type = kwargs['type']
        self.startX = float(kwargs['StartX'])
        self.startY = float(kwargs['StartY'])
        self.endX = float(kwargs['EndX'])
        self.endY = float(kwargs['EndY'])

class Line(D_type):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

class Arc(D_type):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.radius = float(kwargs['Radius'])
        self.sAngle = float(kwargs['SAngle'])
        self.eAngle = float(kwargs['EAngle'])
        self.direction = kwargs['Direction']   
        self.centerX = float(kwargs['CenterX'])
        self.centerY = float(kwargs['CenterY'])

class Shape:
    def __init__(self, shape_info:dict) -> None:
        ## raw dict
        self.shape_info = shape_info
        
        ## split raw dict
        self.type = shape_info['type']
        self.startX = shape_info['StartX']
        self.startY = shape_info['StartY']
        self.endX = shape_info['EndX']
        self.endY = shape_info['EndY']
        self.radius = shape_info['Radius']
        self.sAngle = shape_info['SAngle']
        self.eAngle = shape_info['EAngle']
        self.direction = shape_info['Direction']
        self.centerX = shape_info['CenterX']
        self.centerY = shape_info['CenterY']        
        
        ## processed data
        self.lines, self.arcs = self._parsing_component(self.shape_info)        
        
    @staticmethod
    def _parsing_component(shape_info):
        line_list = []
        arc_list = []

        draw_component_list = [dict(zip(shape_info.keys(), values)) for values in list(zip(*shape_info.values()))]

        for draw_component in draw_component_list:
            if draw_component['type'] == 'D_LineType':
                line_list.append(Line(**draw_component))
            elif draw_component['type'] == 'D_ArcType':
                arc_list.append(Arc(**draw_component))
        return line_list, arc_list

class Net:
    def __init__(self, net_info:dict) -> None:
        self.placed_layer = net_info['PlacedLayer']
        self.name = net_info['Name']
        self.pin_no = net_info['PinNo']

class Component:
    def __init__(self, component_info:dict) -> None:
        self.part_number = int(component_info['PartNo'])
        self.name = component_info['Name']
        self.placed_layer = component_info['PlacedLayer']
        self.x = float(component_info['X'])
        self.y = float(component_info['Y'])
        self.angle = float(component_info['Angle'])
        self.ecad_angle = float(component_info['ECADAngle'])
        self.pin_num = int(component_info['Pin_Num'])
        self.height = float(component_info['Height']) if component_info['Height'] != None else None
        self.part_name = component_info['PartName']
        self.ecad_part_name = component_info['ECADPartName']
        self.package_name = component_info['PackageName']
        self.component_shape = Shape(component_info['CompArea_Top'])
        self.component_area_bottom = Shape(component_info['CompArea_Bottom'])
        self.component_prohibit_area_top = Shape(component_info['CompProhibitArea_Top'])
        self.component_prohibit_area_bottom = Shape(component_info['CompProhibitArea_Bottom'])
        self.hole_area = Shape(component_info['HoleArea'])
        self.pin_dict = component_info['PinDict']
        self.fixed = component_info['Fixed']
        self.group = component_info['Group']

import cv2


class PCB:
    def __init__(self, pcb_info:dict) -> None:
        self.pcb_info = pcb_info
        self.file_name = pcb_info['FileName']
        self.file_format = pcb_info['FileFormat']
        self.board = Shape(pcb_info['BOARD_FIGURE'])
        self.hole_area = Shape(pcb_info['HoleArea'])
        self.prohibit_area = Shape(pcb_info['ProhibitArea'])
        self.component_dict = dict(zip(pcb_info['ComponentDict'].keys(), [Component(comp) for comp in list(pcb_info['ComponentDict'].values())]))
        self.net_list = dict(zip(pcb_info['NetDict'].keys(), [Net(net_info) for net_info in list(pcb_info['NetDict'].values())]))
    
    # def show(self):
        
    
class Parser:
    def __init__(self, path):
        
        if isinstance(path, str):
            self.path = Path(path)
        
        with open(self.path, 'r') as f:
            self.json = json.load(f)
        
        self.pcb_list = self._parsing()
        
        
    def _parsing(self) -> list:
        pcb_info_list = list(self.json.values())
        return [PCB(pcb_info) for pcb_info in pcb_info_list]
        
        
if __name__=="__main__": 
    
    parser = Parser("./data/sample_data.json")

    print(parser.parsing())
    
