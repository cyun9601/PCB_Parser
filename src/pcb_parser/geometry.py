from abc import *
from matplotlib.patches import Arc as mpl_Arc
from matplotlib.patches import Rectangle as mpl_Rect
from matplotlib.lines import Line2D
from .abs import Object
import math
import numpy as np 
from typing import Union  
import cv2
from .utils import floodfill
import copy 
 
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
    
    def __eq__(self, other) -> bool:
        if self.x == other.x and self.y == other.y:
            return True  
        else: 
            return False
    
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
            
        if self.start == self.end: 
            self.sAngle = 0.0
            self.eAngle = 360.0
  
    def __repr__(self) -> str:
        return f'Arc({self.start}, {self.end})'
           
    @property 
    def min_x(self): 
        min_x, max_x, min_y, max_y = self.bounding_box
        return min_x
    
    @property 
    def max_x(self): 
        min_x, max_x, min_y, max_y = self.bounding_box
        return max_x
    
    @property 
    def min_y(self): 
        min_x, max_x, min_y, max_y = self.bounding_box
        return min_y
    
    @property 
    def max_y(self): 
        min_x, max_x, min_y, max_y = self.bounding_box
        return max_y
    
    @property
    def bounding_box(self):
        x = [i.x for i in self.ext_points()] 
        y = [i.y for i in self.ext_points()]
        return min(x), max(x), min(y), max(y)
    
    @property
    def w(self):
        raise NotImplementedError
    
    @property
    def h(self):
        raise NotImplementedError
            
    def draw_mat(self, ax, shift_x=0, shift_y=0, bbox=False, color='k'):
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
        
        if bbox:
            ax.add_patch(mpl_Rect((self.min_x, self.min_y), self.w, self.h, color=color))
        
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
    
    def ext_points(self, delta = 0.05) -> list[Point]:
        points = []
            
        if self.direction == 'CCW': 
            if self.start == self.end: 
                sAngle = 360
                eAngle = 0
            else:
                sAngle, eAngle = self.eAngle, self.sAngle
                if eAngle > sAngle: 
                    eAngle -= 360
            
            cur_angle = sAngle 
            while cur_angle >= eAngle: 
                angle_rad = math.radians(cur_angle)
                x = self.center.x + self.radius * math.cos(angle_rad)
                y = self.center.y + self.radius * math.sin(angle_rad)
                points.append(Point(x, y))
                cur_angle -= delta
            return points
                
        elif self.direction == 'CW' or None: 
            if self.start == self.end : 
                sAngle = 360
                eAngle = 0
            else: 
                sAngle, eAngle = self.sAngle, self.eAngle
                if eAngle > sAngle: 
                    eAngle -= 360
            
            cur_angle = sAngle
            while cur_angle >= eAngle:
                angle_rad = math.radians(cur_angle)
                x = self.center.x + self.radius * math.cos(angle_rad)
                y = self.center.y + self.radius * math.sin(angle_rad)
                points.append(Point(x, y))
                cur_angle -= delta
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

    def __add__(self, other):
        return Polygon([self.lines + other.lines, self.arcs + other.arcs])
        
    @property 
    def min_x(self):
        obj = []
        if len(self) > 0:
            [obj.append(line.min_x) for line in self.lines]
            [obj.append(arc.min_x) for arc in self.arcs]
            return min(obj)
        else: 
            return None 
    
    @property 
    def max_x(self):
        obj = []
        if len(self) > 0:
            [obj.append(line.max_x) for line in self.lines]
            [obj.append(arc.max_x) for arc in self.arcs]
            return max(obj)
        else: 
            return None 
    
    @property 
    def min_y(self):
        obj = []
        if len(self) > 0:
            [obj.append(line.min_y) for line in self.lines]
            [obj.append(arc.min_y) for arc in self.arcs]
            return min(obj)
        else:
            return None 
    
    @property 
    def max_y(self):
        obj = []
        if len(self) > 0:
            [obj.append(line.max_y) for line in self.lines]
            [obj.append(arc.max_y) for arc in self.arcs]
            return max(obj)
        else: 
            return None 
    
    @property 
    def center(self) -> 'Point':
        return Point((self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2)
    
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
    
    def draw_cv(self, resolution=0.05, fill='in') -> np.array:
        
        """
        Shape 의 cv 
        
        - Input -
        img: None일 때는 부품의 크기에 맞는 이미지 생성 
        fill: 'in', 'out'
        
        - Output -
        """
        
        # Line 과 Arc가 존재하지 않으면 None 반환 
        if len(self) == 0: 
            return None 
        
        # 기존에 그린게 있으면 해당 값을 반환
        if 'self.cv_img' in locals(): 
            if (self.cv_resolution == resolution) & (self.cv_fill == fill):
                return self.cv_img
        
        # 원점으로 이동 
        polygon = self.move(-self.min_x, -self.min_y)

        h = int(round(polygon.h / resolution, 0)) + 1 
        w = int(round(polygon.w / resolution, 0)) + 1
        polygon_img = np.ones((h, w)) * 255
        polygon_img = polygon_img.astype(np.uint8)
            
        # Draw line 
        for line in polygon.lines:
            start_x = int(round(line.start.x / resolution, 0))
            start_y = h - 1 - int(round(line.start.y / resolution, 0))
            end_x = int(round(line.end.x / resolution, 0))
            end_y = h - 1 - int(round(line.end.y / resolution, 0))        
            polygon_img = cv2.line(polygon_img, (start_x, start_y), (end_x, end_y), color = (0, 0, 0), thickness=1)

        # Draw arc
        for arc in polygon.arcs:
            centerX = int(round(arc.centerX / resolution, 0))
            centerY = h - 1 - int(round(arc.centerY / resolution, 0))
            radius = int(round(arc.radius / resolution, 0))
            
            if arc.start == arc.end:
                theta1 = 0
                theta2 = 360
            elif arc.direction == 'CW' or arc.direction == None:
                theta1 = 360 - arc.sAngle
                theta2 = 360 - arc.eAngle
                if theta1 > theta2: 
                    theta2 = theta2 + 360
            elif arc.direction == 'CCW':
                theta1 = 360 - arc.eAngle
                theta2 = 360 - arc.sAngle
                if theta1 > theta2:
                    theta2 = theta2 + 360
            
            polygon_img = cv2.ellipse(polygon_img,
                              center = (centerX, centerY),
                              axes = (radius, radius),
                              angle = 0,
                              startAngle = theta1,
                              endAngle = theta2,
                              color = (0, 0, 0),
                              thickness = 1)
        
        # Polygon floodfill
        if fill:
            polygon_img = floodfill(polygon_img, fill_area=fill)

        self.cv_resolution = resolution
        self.cv_fill = fill 
        self.cv_img = polygon_img
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
        else:
            NotImplementedError

    def draw_cv(self, resolution:float=0.05, fill='in') -> tuple[np.array, np.array]:
        # 기존에 그린게 있으면 해당 값을 반환
        if 'self.cv_top_img' in locals(): 
            if (self.cv_resolution == resolution) & (self.cv_fill == fill):
                return self.cv_top_img
        if 'self.cv_bottom_img' in locals(): 
            if (self.cv_resolution == resolution) & (self.cv_fill == fill):
                return self.cv_bottom_img
        
        total_area = self.top_area + self.bottom_area
        
        total_h = int(round(total_area.h / resolution, 0)) + 1
        total_w = int(round(total_area.w / resolution, 0)) + 1
        
        # TOP
        total_top_img = np.ones((total_h, total_w)) * 255
        total_top_img = total_top_img.astype(np.uint8)

        top_img = self.top_area.draw_cv(resolution)
        
        ## Component의 원점 매핑 시 BBox 계산. 
        top_moved_min_x = self.top_area.min_x - total_area.min_x
        top_moved_max_x = self.top_area.max_x - total_area.min_x
        top_moved_min_y = self.top_area.min_y - total_area.min_y 
        top_moved_max_y = self.top_area.max_y - total_area.min_y 
        
        ## Pixel 영역에서의 BBox 영역 매핑 
        top_min_pix_h = total_h - 1 - int(round((top_moved_max_y / resolution), 0))
        top_max_pix_h = total_h - 1 - int(round((top_moved_min_y / resolution), 0))
        top_min_pix_w = int(round((top_moved_min_x / resolution), 0))
        top_max_pix_w = int(round((top_moved_max_x / resolution), 0))
        
        ## 이미지 삽입 
        total_top_img[top_min_pix_h:top_min_pix_h+top_img.shape[0], top_min_pix_w:top_min_pix_w+top_img.shape[1]] = top_img 
    
        # BOTTOM
        total_bottom_img = np.ones((total_h, total_w)) * 255
        total_bottom_img = total_bottom_img.astype(np.uint8)
        
        bottom_img = self.bottom_area.draw_cv(resolution)
        
        ## Component의 원점 매핑 시 BBox 계산.
        bottom_moved_min_x = self.bottom_area.min_x - total_area.min_x
        bottom_moved_max_x = self.bottom_area.max_x - total_area.min_x
        bottom_moved_min_y = self.bottom_area.min_y - total_area.min_y 
        bottom_moved_max_y = self.bottom_area.max_y - total_area.min_y 
    
        ## Pixel 영역에서의 BBox 영역 매핑 
        bottom_min_pix_h = total_h - 1 - int(round((bottom_moved_max_y / resolution), 0))
        bottom_max_pix_h = total_h - 1 - int(round((bottom_moved_min_y / resolution), 0))
        bottom_min_pix_w = int(round((bottom_moved_min_x / resolution), 0))
        bottom_max_pix_w = int(round((bottom_moved_max_x / resolution), 0))
        
        ## 이미지 삽입 
        total_bottom_img[bottom_min_pix_h:bottom_min_pix_h + bottom_img.shape[0], bottom_min_pix_w:bottom_min_pix_w + bottom_img.shape[1]] = bottom_img 

        self.cv_top_img = total_top_img    
        self.cv_bottom_img = total_bottom_img   
        self.cv_resolution = resolution
        
        return self.cv_top_img, self.cv_bottom_img     
        
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
    def bounding_box(self):
        return self.min_x, self.max_x, self.min_y, self.max_y
    
    def get_cv_img_center(self, size:tuple, resolution:float = 0.05, fill:bool=True) -> np.array:
        """
        - Input -
        size(tuple): Background 이미지의 크기(tuple)
        resolution(float): 
        
        - Output -
        """
        
        top_img = np.ones(size) * 255
        bottom_img = np.ones(size) * 255
        
        base_pix_h = top_img.shape[0]
        base_pix_w = top_img.shape[1]
        
        if 'self.cv_top_img' not in locals():
            self.cv_top_img, self.cv_bottom_img = self.draw_cv(resolution, fill)
        comp_top_img, comp_bottom_img = self.cv_top_img, self.cv_bottom_img
        
        start_h = int(round(base_pix_h / 2 - (comp_top_img.shape[0] / 2), 0))
        end_h = int(round(base_pix_h / 2 + (comp_top_img.shape[0] / 2), 0))
        
        start_w = int(round(base_pix_w / 2 - (comp_top_img.shape[1] / 2), 0))
        end_w = int(round(base_pix_w / 2 + (comp_top_img.shape[1] / 2), 0))
        
        ## TOP 이미지 삽입
        top_img[start_h:end_h, start_w:end_w] = comp_top_img 
        
        ## BOTTOM 이미지 삽입
        bottom_img[start_h:end_h, start_w:end_w] = comp_bottom_img 
        return top_img, bottom_img

        
def merge_polygon(base_img:np.array, background:Polygon, foreground:Polygon, resolution = 0.05, inplace = False) -> np.array:
    if inplace == False:
        base_img = copy.deepcopy(base_img)
    
    back_pix_h = int(round(background.h / resolution, 0)) + 1
    back_pix_w = int(round(background.w / resolution, 0)) + 1
    
    ## Component의 원점 매핑 시 BBox 계산. 
    moved_min_x = foreground.min_x - background.min_x
    moved_max_x = foreground.max_x - background.min_x
    moved_min_y = foreground.min_y - background.min_y 
    moved_max_y = foreground.max_y - background.min_y 

    ## Pixel 영역에서의 BBox 영역 매핑 
    min_pix_h = back_pix_h - 1 - int(round((moved_max_y / resolution), 0))
    max_pix_h = back_pix_h - 1 - int(round((moved_min_y / resolution), 0))
    min_pix_w = int(round((moved_min_x / resolution), 0))
    max_pix_w = int(round((moved_max_x / resolution), 0))

    ## 이미지 삽입 
    partial_base_img = base_img[min_pix_h:min_pix_h+foreground.cv_img.shape[0], min_pix_w:min_pix_w+foreground.cv_img.shape[1]]
    if ((partial_base_img == 0) & (foreground.cv_img == 0)).sum() > 0: 
        collision = True
    else:
        collision = False
    base_img[min_pix_h:min_pix_h+foreground.cv_img.shape[0], min_pix_w:min_pix_w+foreground.cv_img.shape[1]] = foreground.cv_img 
    return base_img, collision