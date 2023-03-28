from abc import *
from matplotlib.patches import Arc as mpl_Arc
from matplotlib.lines import Line2D
from .abs import Object
import math
import numpy as np 
from typing import Union  
import cv2 



class Point(Object):
    def __init__(self, x, y):
        self.x = x 
        self.y = y 
        
    def min_x(self):
        return self.x
    
    def max_x(self):
        return self.x
    
    def min_y(self):
        return self.y
    
    def max_y(self):
        return self.y
    
    def bounding_box(self):
        return self.x, self.y, self.x, self.y
    
    def w(self):
        return 0
    
    def h(self):
        return 0

    def draw(self):
        raise NotImplementedError
    
    def move(self, x, y, inplace=False) -> 'Point':
        if inplace == True : 
            self.x += x 
            self.y += y
            return self
        else:
            return Point(self.x + x, self.y + y) 
    
    def move_to(self, x, y) -> 'Point':
        self.x = x 
        self.y = y
        return Point(x, y)
    
    def to_tuple(self) -> tuple:
        return (self.x, self.y)
    
    def center(self) -> 'Point':
        return self
    
    def __add__(self, other) -> 'Point':
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other) -> 'Point':
        return Point(self.x - other.x, self.y - other.y)
    
    def __truediv__(self, other) -> 'Point':
        if type(other) in [int, float]: 
            return Point(self.x / other, self.y / other)
        else: 
            raise NotImplementedError
    
    def __repr__(self) -> str:
        return f'Point({self.x}, {self.y})'
    
class Curve(Object): # dataclass 
    def __init__(self, data) -> None:
        if type(data) == dict: 
            self.start = Point(float(data['StartX']), float(data['StartY']))
            self.end = Point(float(data['EndX']), float(data['EndY']))
        elif type(data) in [list, tuple]:
            self.start = data[0]
            self.end = data[1]
    
    def min_x(self):
        return min()
    
    @abstractmethod
    def ext_points(self):
        ...
    
    @abstractmethod
    def center(self):
        ...
        
    def draw(self):
        raise NotImplementedError


class Line(Curve):
    
    def __init__(self, data) -> None:
        Curve.__init__(self, data)
    
    def __repr__(self) -> str:
        return f'Line({self.start}, {self.end})'
        
    @property 
    def min_x(self):
        return min(self.start.x, self.end.x)

    @property
    def max_x(self):
        return max(self.start.x, self.end.x)
    
    @property 
    def min_y(self):
        return min(self.start.y, self.end.y)
    
    @property 
    def max_y(self):
        return max(self.start.y, self.end.y)
    
    @property 
    def center(self):
        return (self.start + self.end) / 2

    @property
    def bounding_box(self):
        raise NotImplementedError
    
    @property
    def w(self):
        return self.max_x - self.min_x

    @property
    def h(self):
        return self.max_y - self.min_y

    @property 
    def length(self):
        return math.sqrt((self.end.x - self.start.x) ** 2 + (self.end.y - self.start.y) ** 2)

    def draw_mat(self, ax, shift_x:float=0, shift_y:float=0, color='k'):
        moved_ = self.move(shift_x, shift_y)
        l = Line2D([moved_.start.x, moved_.end.x], [moved_.start.y, moved_.end.y], color=color)
        ax.add_line(l)
        
    def move(self, x, y, inplace = False) -> 'Line':
        if inplace == False:
            return Line([Point(self.start.x + x, self.start.y + y), Point(self.end.x + x, self.end.y + y)])
        else: 
            self.start.x += x
            self.end.x += x
            self.start.y += y
            self.end.y += y
            return self
    
    def move_to(self, point:Point):
        raise NotImplementedError
           
    def ext_points(self, delta=0.01) -> list[Point]:
        
        n_points = int(np.ceil(self.length / delta))
    
        x_list = np.linspace(self.start.x, self.end.x, n_points)
        y_list = np.linspace(self.start.y, self.end.y, n_points)
        
        points = []
        for x, y in zip(x_list, y_list):
            points.append(Point(x, y))
        return points 
                
class Arc(Curve):
    def __init__(self, data, **kwargs) -> None:
        Curve.__init__(self, data)
        
        if type(data) == dict: 
            if data['Radius'] != None: self.radius = float(data['Radius'])
            if data['SAngle'] != None: self.sAngle = float(data['SAngle'])
            if data['EAngle'] != None: self.eAngle = float(data['EAngle'])
            self.direction = data['Direction'] if data['Direction'] != None else None
            if data['CenterX'] != None:
                self.centerX = float(data['CenterX'])
            if data['CenterY'] != None:
                self.centerY = float(data['CenterY'])
                
        elif type(data) in [list, tuple]:
            self.radius = float(kwargs['radius'])
            self.sAngle = float(kwargs['sAngle'])
            self.eAngle = float(kwargs['eAngle'])
            self.direction = kwargs['direction'] if kwargs['direction'] != None else None
            self.centerX = float(kwargs['centerX']) 
            self.centerY = float(kwargs['centerY'])
            
    def __repr__(self) -> str:
        return f'Arc({self.start}, {self.end})'
            
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
        return self.min_x, self.max_x, self.min_y, self.max_y
    
    @property
    def w(self):
        raise NotImplementedError
    
    @property
    def h(self):
        raise NotImplementedError
            
    def draw_mat(self, ax, shift_x=0, shift_y=0, color='k'):
        center = self.move(shift_x, shift_y).center
        width = self.radius * 2
        height = self.radius * 2
        angle = 0
        
        if self.direction == 'CW' or self.direction == None:
            theta1 = self.eAngle
            theta2 = self.sAngle
        elif self.direction == 'CCW':
            theta1 = self.sAngle
            theta2 = self.eAngle
        
        ax.add_patch(mpl_Arc(center.to_tuple(), width, height, angle, theta1, theta2, color=color))
        
        
    def move(self, x, y, inplace = False) -> 'Arc':
        if inplace == False: 
            return self.copy().move(x, y, inplace = True) # Point(self.centerX + shift[0], self.centerY + shift[1])
        else :
            self.start = self.start.move(x, y, inplace)
            self.end = self.end.move(x, y, inplace)
            self.centerX += x
            self.centerY += y
            return self
        
    def move_to(self) -> 'Arc':
        raise NotImplementedError    
    
    def ext_points(self, delta = 0.1) -> list[Point]:
        if self.sAngle > self.eAngle:
            self.sAngle, self.eAngle = self.eAngle, self.sAngle
            
        points = []
        cur_angle = self.sAngle
        while cur_angle <= self.eAngle: 
            angle_rad = math.radians(cur_angle)
            x = self.center.x + self.radius * math.cos(angle_rad)
            y = self.center.y + self.radius * math.sin(angle_rad)
            points.append(Point(x, y))
            cur_angle += delta            
        return points
    
    @property
    def center(self):
        return Point(self.centerX, self.centerY)
    
class Polygon(Object):
    def __init__(self, data:Union[dict, list, tuple]) -> None:
        if type(data) == dict: 
            self.lines, self.arcs = self.parsing_shape(data)        
        elif (type(data) in [list, tuple]) and (len(data) == 2):
            self.lines, self.arcs = data
        
    def __len__(self):
        return len(self.lines) + len(self.arcs)
    
    # def _object_checker(func): # decorator 
    #     def wrapper(self):
    #         if self.__len__() > 0: 
    #             return func
    #         else:
    #             return None 
    #     return wrapper
    
    def __add__(self, other):
        return Polygon([self.lines + other.lines, self.arcs + other.arcs])
        
    @property 
    def min_x(self):
        if self.__len__() > 0:
            return min([line.min_x for line in self.lines])
        else: 
            return None 
    
    @property 
    def max_x(self):
        if self.__len__() > 0:
            return max([line.max_x for line in self.lines])
        else: 
            return None 
    
    @property 
    def min_y(self):
        if self.__len__() > 0:
            return min([line.min_y for line in self.lines])
        else:
            return None 
    
    @property 
    def max_y(self):
        if self.__len__() > 0:
            return max([line.max_y for line in self.lines])
        else: 
            return None 
    
    @property 
    def center(self) -> 'Point':
        return Point((self.min_x + self.max_x), (self.min_y + self.max_y))
    
    @property
    def bounding_box(self):
            return self.min_x, self.max_x, self.min_y, self.max_y
    
    @property
    def w(self):
        return self.max_x - self.min_x
    
    @property 
    def h(self):
        return self.max_y - self.min_y
    
    def draw_mat(self, ax, shift_x=0, shift_y=0, color='k'):
        for line in self.lines:
            line.draw(ax, shift_x, shift_y, color=color)
        for arc in self.arcs:
            arc.draw(ax, shift_x, shift_y, color=color)
    
    #def draw_cv(self, arr, color=None):
        #line에서 가장 작은 값을 뽑기    
        #min(#for line in self.lines:
        #    arr = line.draw_cv(arr)
            
            
            
        #for arc in self.arcs:
            #arr = arc.draw_cv(arr)
            
            
            
    #    return arr
    
    def move(self, x, y, inplace=False) -> 'Polygon':
        self.lines = [line.move(x, y, inplace) for line in self.lines]
        self.arcs = [arc.move(x, y, inplace) for arc in self.arcs]
        return Polygon([self.lines, self.arcs])
    
    def move_to(self) -> 'Polygon':
        raise NotImplementedError
    
    @staticmethod
    def parsing_shape(area_info):
        line_list = []
        arc_list = []

        draw_component_list = [dict(zip(area_info.keys(), values)) for values in list(zip(*area_info.values()))]

        for draw_component in draw_component_list:
            if draw_component['type'] == 'D_LineType':
                line_list.append(Line(draw_component))
            elif draw_component['type'] == 'D_ArcType':
                arc_list.append(Arc(draw_component))
        return line_list, arc_list
    
class Component:
    def __init__(self, component_info:dict) -> None:
        self.part_number = int(component_info['PartNo'])
        self.name = component_info['Name']
        self.placed_layer = component_info['PlacedLayer']
        self.center = Point(float(component_info['X']), float(component_info['Y'])) 
        self.angle = float(component_info['Angle'])
        self.ecad_angle = float(component_info['ECADAngle'])
        self.pin_num = int(component_info['Pin_Num'])
        self.height = float(component_info['Height']) if component_info['Height'] != None else None
        self.part_name = component_info['PartName']
        self.ecad_part_name = component_info['ECADPartName']
        self.package_name = component_info['PackageName']
        self.top_area = Polygon(component_info['CompArea_Top']).move(self.center.x, self.center.y) #중심축에서
        self.bottom_area = Polygon(component_info['CompArea_Bottom']).move(self.center.x, self.center.y)
        self.top_prohibit_area = Polygon(component_info['CompProhibitArea_Top']).move(self.center.x, self.center.y)
        self.bottom_prohibit_area = Polygon(component_info['CompProhibitArea_Bottom']).move(self.center.x, self.center.y)
        self.hole_area = Polygon(component_info['HoleArea']).move(self.center.x, self.center.y)
        self.pin_dict = component_info['PinDict']
        self.fixed = component_info['Fixed']
        self.group = component_info['Group']
        # self.outline_img = self.get_outline_img() # Outline
        #self.cv_image = [ if component_info(['CompArea_Top']]np.zeros((int(round(self.height/0.005,0)),int(round(self.w/0.005,0)),3), dtype=np.uint8) #list [앞 , 뒤]
        #p_h = int((self.top_area + self.bottom_area).h/0.005)
        #p_w = int((self.top_area + self.bottom_area).w/0.005)
        #arr = np.ones((p_h,p_w,3), dtype=np.uint8)*255    
        #self.cv_image = [self.top_area.draw_cv(arr), self.bottom_area.draw_cv(arr)]
        
        #폴리곤 draw_cv 메소드 (self,arr, 최소픽셀단위)

    #def _draw_cv(self):
    #    p_h = int(round((self.top_area + self.bottom_area).h/0.005),0)
    #    p_w = int(round((self.top_area + self.bottom_area).w/0.005),0)
    #    arr = np.ones((p_h,p_w,3), dtype=np.uint8)*255    
    #    area = self.top_area+self.bottom_area
    #    bbox_x , = self.bounding_box
        
        
    #    return  
        
    
    
    
    def draw(self, ax, layer, shift_x=0, shift_y=0, color='k'): 
        if layer == 'TOP':
            self.top_area.draw(ax, shift_x=shift_x, shift_y=shift_y, color=color)
        elif layer == 'BOTTOM':
            self.bottom_area.draw(ax, shift_x=shift_x, shift_y=shift_y, color=color)
        self.hole_area.draw(ax, shift_x=shift_x, shift_y=shift_y, color=color)

    def move(self, x, y):
        raise NotImplementedError
        
    def move_to(self, x, y):
        raise NotImplementedError
    
    @property    
    def min_x(self):
        return (self.top_area + self.bottom_area).min_x
    
    @property
    def max_x(self):
        return (self.top_area + self.bottom_area).max_x
    
    @property    
    def min_y(self):
        return (self.top_area + self.bottom_area).min_y
    
    @property
    def max_y(self):
        return (self.top_area + self.bottom_area).max_y
    
    @property
    def get_size(self):
        return self.min_x, self.max_x, self.min_y, self.max_y
    
    # def get_outline_img(self):
        # img = np.zeros()
        # pass