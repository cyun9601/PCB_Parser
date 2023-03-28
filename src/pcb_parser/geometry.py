from abc import *
from matplotlib.patches import Arc as mpl_Arc
from matplotlib.lines import Line2D
from .abs import Object
import math
import numpy as np 
from typing import Union  
import cv2
from .utils import floodfill
 
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

    def draw_mat(self):
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
        
    def draw_mat(self):
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
        return self.min_x, self.max_x, self.min_y, self.max_y
    
    @property
    def w(self):
        return self.max_x - self.min_x

    @property
    def h(self):
        return self.max_y - self.min_y

    @property 
    def length(self):
        return math.sqrt((self.end.x - self.start.x) ** 2 + (self.end.y - self.start.y) ** 2)

    def draw_mat(self, ax, shift_x:0, shift_y:0, color='k'):
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
            line.draw_mat(ax, shift_x, shift_y, color=color)
        for arc in self.arcs:
            arc.draw_mat(ax, shift_x, shift_y, color=color)
    
    def draw_cv(self, resolution=0.05, img:np.array=None) -> np.array:
        
        '''
        Shape 의 cv 
        
        - Input -
        img: None일 때는 부품의 크기에 맞는 이미지 생성 
        
        - Output -
        
        '''
        
        # Line 과 Arc 속성이 존재하지 않으면 None 반환 
        if len(self) == 0: 
            return None 
        
        if img == None: 
            # 원점으로 이동 
            polygon = self.move(-self.min_x, -self.min_y)

            h = int(round(polygon.h / resolution, 0))
            w = int(round(polygon.w / resolution, 0))
            img = np.ones((w, h)) * 255
            img = img.astype(np.uint8)
        else: 
            polygon = self.copy()

        # Draw line 
        for line in polygon.lines:
            start_x = int(round(line.start.x / resolution))
            start_y = int(round(line.start.y / resolution))
            end_x = int(round(line.end.x / resolution))
            end_y = int(round(line.end.y / resolution))        
            img = cv2.line(img, (start_x, h-start_y), (end_x, h-end_y), color = (0, 0, 0), thickness=1)

        # Draw arc
        
        self.cv_img = img
        self.cv_img = floodfill(self.cv_img)
        return self.cv_img
        
    def move(self, x, y, inplace=False) -> 'Polygon':
        if inplace:
            self.lines = [line.move(x, y, inplace) for line in self.lines]
            self.arcs = [arc.move(x, y, inplace) for arc in self.arcs]
            return self
        else: 
            lines = [line.move(x, y, inplace) for line in self.lines]
            arcs = [arc.move(x, y, inplace) for arc in self.arcs]
            return Polygon([lines, arcs])
    
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
    def __init__(self, data:dict) -> None:
        
        if type(data) == dict: 
            self.part_number = int(data['PartNo'])
            self.name = data['Name']
            self.placed_layer = data['PlacedLayer']
            self.center = Point(float(data['X']), float(data['Y'])) 
            self.angle = float(data['Angle'])
            self.ecad_angle = float(data['ECADAngle'])
            self.pin_num = int(data['Pin_Num'])
            self.height = float(data['Height']) if data['Height'] != None else None
            self.part_name = data['PartName']
            self.ecad_part_name = data['ECADPartName']
            self.package_name = data['PackageName']
            self.top_area = Polygon(data['CompArea_Top']).move(self.center.x, self.center.y)
            self.bottom_area = Polygon(data['CompArea_Bottom']).move(self.center.x, self.center.y)
            self.top_prohibit_area = Polygon(data['CompProhibitArea_Top']).move(self.center.x, self.center.y)
            self.bottom_prohibit_area = Polygon(data['CompProhibitArea_Bottom']).move(self.center.x, self.center.y)
            self.hole_area = Polygon(data['HoleArea']).move(self.center.x, self.center.y)
            self.pin_dict = data['PinDict']
            self.fixed = data['Fixed']
            self.group = data['Group']
            # self.outline_img = self.get_outline_img() # Outline
        else : 
            NotImplementedError

    def draw_cv(self, resolution:float=0.05, img:np.array=None) -> tuple(np.array, np.array):
        if img == None: 
            
            h = int(round((self.top_area + self.bottom_area).h / resolution, 0))
            w = int(round((self.top_area + self.bottom_area).w / resolution, 0))
            img = np.ones((w, h)) * 255
            img = img.astype(np.uint8)

            top_img = self.top_area.draw_cv(resolution=resolution)
            bottom_img = self.bottom_area.draw_cv(resolution)
            
            img[:, :] = top_img 
            
            
            

    def draw_mat(self, ax, layer, shift_x=0, shift_y=0, color='k'): 
        if layer == 'TOP':
            self.top_area.draw_mat(ax, shift_x=shift_x, shift_y=shift_y, color=color)
        elif layer == 'BOTTOM':
            self.bottom_area.draw_mat(ax, shift_x=shift_x, shift_y=shift_y, color=color)
        self.hole_area.draw_mat(ax, shift_x=shift_x, shift_y=shift_y, color=color)


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