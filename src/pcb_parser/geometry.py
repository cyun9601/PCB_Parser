from abc import *
from matplotlib.patches import Arc as mpl_Arc
from matplotlib.lines import Line2D
import os 
from .abs import Draw_type
import cv2
import numpy as np 

class Geometry: # dataclass 
    def __init__(self, arg_dict) -> None:
        self.type = arg_dict['type']
        self.startX = float(arg_dict['StartX'])
        self.startY = float(arg_dict['StartY'])
        self.endX = float(arg_dict['EndX'])
        self.endY = float(arg_dict['EndY'])
        if arg_dict['Radius'] != None: self.radius = float(arg_dict['Radius'])
        if arg_dict['SAngle'] != None: self.sAngle = float(arg_dict['SAngle'])
        if arg_dict['EAngle'] != None: self.eAngle = float(arg_dict['EAngle'])
        self.direction = arg_dict['Direction'] if arg_dict['Direction'] != None else None
        if arg_dict['CenterX'] != None: self.centerX = float(arg_dict['CenterX'])
        if arg_dict['CenterY'] != None: self.centerY = float(arg_dict['CenterY'])

class Line(Geometry, Draw_type):
    def __init__(self, arg_dict) -> None:
        Geometry.__init__(self, arg_dict)

    def get_line(self):
        return (self.startX, self.endX), (self.startY, self.endY)

    @property 
    def min_x(self):
        return min(self.startX, self.endX)

    @property
    def max_x(self):
        return max(self.startX, self.endX)
    
    @property 
    def min_y(self):
        return min(self.startY, self.endY)
    
    @property 
    def max_y(self):
        return max(self.startY, self.endY)

    @property
    def bounding_box(self):
        raise NotImplementedError

    @property
    def w(self):
        raise NotImplementedError

    @property
    def h(self):
        raise NotImplementedError

    def draw(self, ax, shift = None, color='k'):
        if shift is not None:
            l = Line2D(*self.translation(shift), color=color)
        else:
            l = Line2D(*self.get_line(), color=color)
        ax.add_line(l)
            
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

    def move(self):
        raise NotImplementedError 
    
    def move_to(self):
        raise NotImplementedError
            
class Arc(Geometry, Draw_type):
    def __init__(self, arg_dict) -> None:
        Geometry.__init__(self, arg_dict)
        
    @property 
    def min_x(self): 
        x_min, y_min, x_max, y_max = self.get_extents().bounds
        return x_min
    
    @property 
    def max_x(self): 
        x_min, y_min, x_max, y_max = self.get_extents().bounds
        return x_max
    
    @property 
    def min_y(self): 
        x_min, y_min, x_max, y_max = self.get_extents().bounds
        return y_min
    
    @property 
    def max_y(self): 
        x_min, y_min, x_max, y_max = self.get_extents().bounds
        return y_max
    
    @property
    def bounding_box(self):
        raise NotImplementedError
    
    @property
    def w(self):
        raise NotImplementedError
    
    @property
    def h(self):
        raise NotImplementedError
            
    def draw(self, ax, shift = None, color='k'):
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
        
        ax.add_patch(mpl_Arc(center, width, height, angle, theta1, theta2, color=color))
        
    def translation(self, shift, inplace = False):
        if inplace == False: 
            return (self.centerX + shift[0], self.centerY + shift[1])
        else :
            self.centerX += shift[0]
            self.centerY += shift[1]
            return self.get_center()
        
    def get_center(self):
        return (self.centerX, self.centerY)
        
    def move(self):
        raise NotImplementedError 
    
    def move_to(self):
        raise NotImplementedError
        
class Area(Draw_type):
    def __init__(self, area_info:dict) -> None:
        self.area_info = area_info
        
        ## processed data
        self.lines, self.arcs = self.parsing_component(self.area_info)        
        
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
    def w(self):
        return self.max_x - self.min_x
    
    @property 
    def h(self):
        return self.max_y - self.min_y
    
    def draw(self, ax, shift=None, color='k'):
        for line in self.lines:
            line.draw(ax, shift=shift, color=color)
        for arc in self.arcs:
            arc.draw(ax, shift=shift, color=color)
    
    def translation(self):
        raise NotImplementedError
    
    def move(self):
        raise NotImplementedError 
    
    def move_to(self):
        raise NotImplementedError
    
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
        # self.outline_img = self.get_outline_img() # Outline 

    @property
    def min_x(self):
        raise NotImplementedError
    
    @property
    def max_x(self):
        raise NotImplementedError
    
    @property
    def min_y(self):
        raise NotImplementedError
    
    @property
    def max_y(self):
        raise NotImplementedError
    
    @property
    def bounding_box(self):
        raise NotImplementedError
    
    @property
    def w(self):
        raise NotImplementedError
    
    @property
    def h(self):
        raise NotImplementedError
    
    def draw(self, ax, shift=None, color='k'): 
        if self.placed_layer == 'TOP':
            self.component_top_area.draw(ax, shift=(self.x, self.y), color=color)
        elif self.placed_layer == 'BOTTOM':
            self.component_bottom_area.draw(ax, shift=(self.x, self.y), color=color)
        self.hole_area.draw(ax, shift=shift, color=color)

    def translation(self):
        raise NotImplementedError

    def move(self, x, y):
        self.x = self.x + x
        self.y = self.y + y 
        
    def move_to(self, center_x, center_y):
        self.x = center_x 
        self.y = center_y 
        
    # def get_outline_img(self):
        # img = np.zeros()
        # pass