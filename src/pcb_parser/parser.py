import json 
from abc import *
import matplotlib.pyplot as plt
import os 
from .geometry import Draw_type, Line, Arc

class Shape(Draw_type):
    def __init__(self, shape_info:dict) -> None:
        ## raw dict
        self.shape_info = shape_info
        
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
        
    def draw(self, ax, shift=None):
        for line in self.lines:
            line.draw(ax, shift=shift)
        for arc in self.arcs:
            arc.draw(ax, shift=shift)
        
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

class Component(Draw_type):
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
        self.component_top_shape = Shape(component_info['CompArea_Top'])
        self.component_bottom_shape = Shape(component_info['CompArea_Bottom'])
        self.component_top_prohibit_shape = Shape(component_info['CompProhibitArea_Top'])
        self.component_bottom_prohibit_shape = Shape(component_info['CompProhibitArea_Bottom'])
        self.hole_area = Shape(component_info['HoleArea'])
        self.pin_dict = component_info['PinDict']
        self.fixed = component_info['Fixed']
        self.group = component_info['Group']

    def draw(self, ax, shift=None): 
        if self.placed_layer == 'TOP':
            self.component_top_shape.draw(ax, shift=(self.x, self.y))
        elif self.placed_layer == 'BOTTOM':
            self.component_bottom_shape.draw(ax, shift=(self.x, self.y))
        self.hole_area.draw(ax, shift=shift)

class Components(Draw_type):
    def __init__(self, components_info:list[dict]) -> None:
        self.components = [Component(comp_info) for comp_info in components_info]
    
    def draw(self, ax, shift=None):
        for component in self.components:
            component.draw(ax, shift=shift)

class PCB(Draw_type):
    def __init__(self, pcb_info:dict) -> None:
        
        self.pcb_info = pcb_info
        self.file_name = pcb_info['FileName']
        self.file_format = pcb_info['FileFormat']
        self.board = Shape(pcb_info['BOARD_FIGURE'])
        self.hole_area = Shape(pcb_info['HoleArea'])
        self.prohibit_area = Shape(pcb_info['ProhibitArea'])
        self.components = Components(pcb_info['ComponentDict'].values()) 
        self.net_list = dict(zip(pcb_info['NetDict'].keys(), [Net(net_info) for net_info in list(pcb_info['NetDict'].values())]))
    
    def draw(self, image_name='./draw.png', shift=None, figsize=(10, 10), dpi=300) -> dict:
        fig = plt.figure(figsize=figsize, dpi=dpi)

        ax = fig.add_subplot(111)
        
        self.board.draw(ax, shift=shift)
        self.hole_area.draw(ax, shift=shift)
        self.components.draw(ax, shift=shift)
        
        # ax.set_title('a) valid')
        ax.set_xlim([0, 60])
        ax.set_ylim([0, 150])
        ax.set_aspect('equal') #, 'box')
        
        plt.savefig(dpi=dpi, fname=image_name)