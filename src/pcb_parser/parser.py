import json 
from abc import *
import matplotlib.pyplot as plt
import os 
from .geometry import Draw_type, Line, Arc

class Area(Draw_type):
    def __init__(self, area_info:dict) -> None:
        ## raw dict
        self.area_info = area_info
        self.type = area_info['type']
        self.startX = area_info['StartX']
        self.startY = area_info['StartY']
        self.endX = area_info['EndX']
        self.endY = area_info['EndY']
        self.radius = area_info['Radius']
        self.sAngle = area_info['SAngle']
        self.eAngle = area_info['EAngle']
        self.direction = area_info['Direction']
        self.centerX = area_info['CenterX'] # center X of arc
        self.centerY = area_info['CenterY'] # center Y of arc       
        
        ## processed data
        self.lines, self.arcs = self.parsing_component(self.area_info)        
        
    def draw(self, ax, shift=None, color='k'):
        for line in self.lines:
            line.draw(ax, shift=shift, color=color)
        for arc in self.arcs:
            arc.draw(ax, shift=shift, color=color)
    
    @property 
    def min_x(self):
        return min([line.min_x for line in self.lines])
    
    @property 
    def max_x(self):
        return max([line.max_x for line in self.lines])
    
    @property 
    def min_y(self):
        return min([line.min_y for line in self.lines])
    
    @property 
    def max_y(self):
        return max([line.max_y for line in self.lines])
    
    @property 
    def bounding_box(self):
        return self.min_x, self.max_x, self.min_y, self.max_y
    
    @property 
    def width(self):
        return self.max_x - self.min_x
    
    @property 
    def height(self):
        return self.max_y - self.min_y
    
    @staticmethod
    def parsing_component(area_info):
        line_list = []
        arc_list = []

        draw_component_list = [dict(zip(area_info.keys(), values)) for values in list(zip(*area_info.values()))]

        for draw_component in draw_component_list:
            if draw_component['type'] == 'D_LineType':
                line_list.append(Line(draw_component))
            elif draw_component['type'] == 'D_ArcType':
                arc_list.append(Arc(draw_component))
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
        self.x = float(component_info['X']) # center X
        self.y = float(component_info['Y']) # center Y
        self.angle = float(component_info['Angle'])
        self.ecad_angle = float(component_info['ECADAngle'])
        self.pin_num = int(component_info['Pin_Num'])
        self.height = float(component_info['Height']) if component_info['Height'] != None else None
        self.part_name = component_info['PartName']
        self.ecad_part_name = component_info['ECADPartName']
        self.package_name = component_info['PackageName']
        self.component_top_area = Area(component_info['CompArea_Top'])
        self.component_bottom_area = Area(component_info['CompArea_Bottom'])
        self.component_top_prohibit_area = Area(component_info['CompProhibitArea_Top'])
        self.component_bottom_prohibit_area = Area(component_info['CompProhibitArea_Bottom'])
        self.hole_area = Area(component_info['HoleArea'])
        self.pin_dict = component_info['PinDict']
        self.fixed = component_info['Fixed']
        self.group = component_info['Group']

    def draw(self, ax, shift=None, color='k'): 
        if self.placed_layer == 'TOP':
            self.component_top_area.draw(ax, shift=(self.x, self.y), color=color)
        elif self.placed_layer == 'BOTTOM':
            self.component_bottom_area.draw(ax, shift=(self.x, self.y), color=color)
        self.hole_area.draw(ax, shift=shift, color=color)

    def move(self, center_x, center_y):
        self.x = center_x 
        self.y = center_y 

    def shift(self, x, y):
        self.x = self.x + x
        self.y = self.y + y 
        
class PCB(Draw_type):
    def __init__(self, pcb_info:dict) -> None:
        self.pcb_info = pcb_info
        self.file_name = pcb_info['FileName']
        self.file_format = pcb_info['FileFormat']
        self.board = Area(pcb_info['BOARD_FIGURE'])
        self.hole_area = Area(pcb_info['HoleArea'])
        self.prohibit_area = Area(pcb_info['ProhibitArea'])
        self.components_dict = {comp_info['PartName']:Component(comp_info) for comp_info in pcb_info['ComponentDict'].values()}
        self.net_list = dict(zip(pcb_info['NetDict'].keys(), [Net(net_info) for net_info in list(pcb_info['NetDict'].values())]))
    
    def draw(self, image_name:str, layer:str, only_fixed:bool=False, shift=None, save=True, figsize=(10, 10), color='k', dpi:int=300) -> dict:
        '''
        
        '''
        fig = plt.figure(figsize=figsize, dpi=dpi)
        ax = fig.add_subplot(111)
        
        self.board.draw(ax, shift=shift, color=color)
        self.hole_area.draw(ax, shift=shift, color=color)
        
        # draw components
        for _, v in self.components_dict.items():
            if v.placed_layer == layer and (not only_fixed or v.fixed):
                v.draw(ax, shift=shift, color=color)
        
        # ax.set_title('a) valid')
        min_x, max_x, min_y, max_y = self.get_pcb_size
        ax.set_xlim([min_x, max_x])
        ax.set_ylim([min_y, max_y])
        ax.set_aspect('equal') #, 'box')
        
        if save: 
            plt.savefig(dpi=dpi, fname=image_name)
        return fig, ax
    
    @property 
    def get_pcb_size(self):
        return self.board.bounding_box
    
    def find_component(self, part_name:str):
        return NotImplementedError