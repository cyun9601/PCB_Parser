import json 
from pathlib import Path
from dataclasses import dataclass
from abc import *
import matplotlib.pyplot as plt
from matplotlib.patches import Arc as mpl_Arc
from matplotlib.lines import Line2D

class Geometry(metaclass = ABCMeta):
    def __init__(self, **kwargs) -> None:
        self.type = kwargs['type']
        self.startX = float(kwargs['StartX'])
        self.startY = float(kwargs['StartY'])
        self.endX = float(kwargs['EndX'])
        self.endY = float(kwargs['EndY'])

    @abstractmethod
    def translation(self):
        ...

class Draw_type(metaclass = ABCMeta):
    @abstractmethod
    def draw(self):
        ...

class Line(Geometry, Draw_type):
    def __init__(self, **kwargs) -> None:
        Geometry.__init__(self, **kwargs)

    def get_line(self):
        return (self.startX, self.endX), (self.startY, self.endY)

    def translation(self, shift, inplace = False):
        assert len(shift) == 2, "shift must be 2-dimension"
        if inplace == False:
            return (self.startX + shift[0], self.endX + shift[0]), (self.startY + shift[1], self.endY + shift[1])
        else: 
            self.startX += shift[0]
            self.endX += shift[0]
            self.startY += shift[1]
            self.endY += shift[1]
            return self.get_line()
    
    def draw(self, ax, shift = None):
        if shift is not None:
            l = Line2D(*self.translation(shift))
        else:
            l = Line2D(*self.get_line())
        ax.add_line(l)
            
class Arc(Geometry, Draw_type):
    def __init__(self, **kwargs) -> None:
        Geometry.__init__(self, **kwargs)
        self.radius = float(kwargs['Radius'])
        self.sAngle = float(kwargs['SAngle'])
        self.eAngle = float(kwargs['EAngle'])
        self.direction = kwargs['Direction']   
        self.centerX = float(kwargs['CenterX'])
        self.centerY = float(kwargs['CenterY'])

    def get_center(self):
        return (self.centerX, self.centerY)
    
    def translation(self, shift, inplace = False):
        if inplace == False: 
            return (self.centerX + shift[0], self.centerY + shift[1])
        else :
            self.centerX += shift[0]
            self.centerY += shift[1]
            return self.get_center() 
            
    def draw(self, ax, shift = None):
        if shift is not None: 
            center = self.translation(shift)
        else : 
            center = self.get_center()
        width = self.radius * 2
        height = self.radius * 2
        angle = 0
        
        if self.direction == 'CW' or self.direction == None:
            theta1 = self.eAngle
            theta2 = self.sAngle
        elif self.direction == 'CCW':
            theta1 = self.sAngle
            theta2 = self.eAngle
        
        ax.add_patch(mpl_Arc(center, width, height, angle, theta1, theta2))
            
class Shape(Draw_type):
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
    
    def draw(self, shift=None, figsize=(10, 10), dpi=300) -> dict:
        fig = plt.figure(1, figsize=figsize, dpi=dpi)

        ax = fig.add_subplot(111)
        
        self.board.draw(ax, shift=shift)
        self.hole_area.draw(ax, shift=shift)
        self.components.draw(ax, shift=shift)
        
        # ax.set_title('a) valid')
        ax.set_xlim([0, 60])
        ax.set_ylim([0, 150])
        ax.set_aspect('equal') #, 'box')
        
        plt.savefig(dpi=dpi, fname='shapely_polygon.png')
    
if __name__=="__main__": 
    
    with open("./data/sample_data.json", 'r') as f:
            data = json.load(f)

    pcb = PCB(list(data.values())[0])
