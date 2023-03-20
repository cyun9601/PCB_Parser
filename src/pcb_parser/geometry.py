from abc import *
from matplotlib.patches import Arc as mpl_Arc
from matplotlib.lines import Line2D
import os 
from .abs import Draw_type

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
    
    def draw(self, ax, shift = None, color='k'):
        if shift is not None:
            l = Line2D(*self.translation(shift), color=color)
        else:
            l = Line2D(*self.get_line(), color=color)
        ax.add_line(l)
            
class Arc(Geometry, Draw_type):
    def __init__(self, arg_dict) -> None:
        Geometry.__init__(self, arg_dict)
        
    def get_center(self):
        return (self.centerX, self.centerY)
    
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
    
    def translation(self, shift, inplace = False):
        if inplace == False: 
            return (self.centerX + shift[0], self.centerY + shift[1])
        else :
            self.centerX += shift[0]
            self.centerY += shift[1]
            return self.get_center()
            
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
        
        
class Area(Draw_type):
    def __init__(self, area_info:dict) -> None:
        self.area_info = area_info
        # self.type = area_info['type']
        # self.startX = area_info['StartX']
        # self.startY = area_info['StartY']
        # self.endX = area_info['EndX']
        # self.endY = area_info['EndY']
        # self.radius = area_info['Radius']
        # self.sAngle = area_info['SAngle']
        # self.eAngle = area_info['EAngle']
        # self.direction = area_info['Direction']
        # self.centerX = area_info['CenterX'] # center X of arc
        # self.centerY = area_info['CenterY'] # center Y of arc       
        
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