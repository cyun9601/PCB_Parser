from abc import *
from matplotlib.patches import Arc as mpl_Arc
from matplotlib.patches import Rectangle as mpl_Rect
from matplotlib.lines import Line2D
from .abs import Object
import math
import numpy as np 
from typing import Union  
import cv2
from .utils import floodfill, img_rot_90, img_folder
import copy 
import os 
from PIL import Image
 
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
    
    def rotation(self, angle:float, center:'Point'=None, inplace:bool=False) -> 'Point':
        if center is None: 
            center = Point(0, 0)
        
        x = self.x - center.x
        y = self.y - center.y
        
        radian = math.pi * (angle/180)
        
        x_new = x * math.cos(radian) - y * math.sin(radian)
        y_new = x * math.sin(radian) + y * math.cos(radian)
        
        x_new += center.x
        y_new += center.y
        
        if inplace == True : 
            self.x = x_new
            self.y = y_new
            return self
        else:
            return Point(x_new, y_new)
    
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
    
class Curve(Object):  
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
        if inplace: 
            self.start.x += x
            self.end.x += x
            self.start.y += y
            self.end.y += y
            return self
        else:
            # return Line([Point(self.start.x + x, self.start.y + y), Point(self.end.x + x, self.end.y + y)])
            return self.copy().move(x, y, inplace = True) 
    
    def move_to(self, point:Point, inplace:bool=False) -> 'Line':
        return self.move(point.x - self.center.x, point.y - self.center.y, inplace)
        
    def ext_points(self, delta=0.01) -> list[Point]:
        
        n_points = int(np.ceil(self.length / delta))
    
        x_list = np.linspace(self.start.x, self.end.x, n_points)
        y_list = np.linspace(self.start.y, self.end.y, n_points)
        
        points = []
        for x, y in zip(x_list, y_list):
            points.append(Point(x, y))
        return points 
              
    def rotation(self, angle:float, center:Point=None, inplace:bool=False) -> 'Line':
        if center is None: 
            center = Point(0, 0)
        
        start = self.start.rotation(angle, center, inplace)
        end = self.end.rotation(angle, center, inplace)
        
        if inplace == True : 
            self.start = start
            self.end = end
            return self
        else:
            return Line([start, end])
                
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
        points = [i for i in self.ext_points()]
        x = [points.x for points in points]
        y = [points.y for points in points]
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
        if inplace:
            self.start = self.start.move(x, y, inplace)
            self.end = self.end.move(x, y, inplace)
            self.centerX += x
            self.centerY += y
            return self
        else: 
            return self.copy().move(x, y, inplace = True) 
        
    def move_to(self, point:Point, inplace=False) -> 'Arc':
        return self.move(point.x - self.center.x, point.y - self.center.y, inplace)
        
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
                
        elif self.direction == 'CW' or self.direction == None: 
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
    
    def rotation(self, angle:float, center:Point=None, inplace:bool = False) -> 'Arc':
        if inplace:
            if center is None: 
                center = self.center
            
            # Start, End 회전
            self.start = self.start.rotation(angle, center, inplace)
            self.end = self.end.rotation(angle, center, inplace)
            
            # center 회전 
            self.centerX, self.centerY = self.center.rotation(angle, center).to_tuple()
            
            # 회전 값에서 sAngle, eAngle 추정
            self.sAngle = math.atan2(self.start.y - self.centerY, self.start.x - self.centerX) * 180 / math.pi
            if self.sAngle < 0:
                self.sAngle += 360
                
            self.eAngle = math.atan2(self.end.y - self.centerY, self.end.x - self.centerX) * 180 / math.pi
            if self.eAngle < 0:
                self.eAngle += 360
            return self
        else: 
            return self.copy().rotation(angle, center, inplace = True)
        
class Polygon(Object):
    def __init__(self, data:Union[dict, list, tuple], p_resolution=0.05) -> None:
        if type(data) == dict: 
            self.lines, self.arcs = self.parsing_shape(data)        
        elif (type(data) in [list, tuple]) and (len(data) == 2):
            self.lines, self.arcs = data
        self.p_resolution = p_resolution
        
    def __len__(self):
        return len(self.lines) + len(self.arcs)

    def __add__(self, other):
        return Polygon([self.lines + other.lines, self.arcs + other.arcs], self.p_resolution)

    def get_cv_img(self):
        if 'self.cv_img' not in locals():
            self.cv_img = self.draw_cv()
        return self.cv_img
        
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
    
    def draw_cv(self, fill='in', fitting=True) -> np.array:
        
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
        
        if fitting:
            # 원점으로 이동 
            polygon = self.move(-self.min_x, -self.min_y)
        else: 
            polygon = self.copy()

        h = int(round(polygon.max_y / self.p_resolution, 0)) + 1 
        w = int(round(polygon.max_x / self.p_resolution, 0)) + 1
        polygon_img = np.ones((h, w)) * 255
        polygon_img = polygon_img.astype(np.uint8)
            
        # Draw line 
        for line in polygon.lines:
            start_x = int(round(line.start.x / self.p_resolution, 0))
            start_y = h - 1 - int(round(line.start.y / self.p_resolution, 0))
            end_x = int(round(line.end.x / self.p_resolution, 0))
            end_y = h - 1 - int(round(line.end.y / self.p_resolution, 0))        
            polygon_img = cv2.line(polygon_img, (start_x, start_y), (end_x, end_y), color = (0, 0, 0), thickness=1)

        # Draw arc
        for arc in polygon.arcs:
            centerX = int(round(arc.centerX / self.p_resolution, 0))
            centerY = h - 1 - int(round(arc.centerY / self.p_resolution, 0))
            radius = int(round(arc.radius / self.p_resolution, 0))
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
    
    def move_to(self, point:Point, inplace=False) -> 'Polygon':
        dist = point - self.center
        return self.move(dist.x, dist.y, inplace)
    
    @staticmethod
    def parsing_shape(area_info):
        line_list = []
        arc_list = []

        draw_component_list = [dict(zip(area_info.keys(), values)) for values in list(zip(*area_info.values()))]

        for draw_component in draw_component_list:
            if draw_component['type'] == 'D_LineType':
                line_list.append(Line(draw_component))
            elif draw_component['type'] == 'D_ArcType':
                # cam 버그 데이터 잡는 부분 
                if (float(draw_component['SAngle']) == 0) and (float(draw_component['EAngle']) == 360):
                    draw_component['StartX'] = float(draw_component['CenterX']) + float(draw_component['Radius'])
                    draw_component['EndX'] = float(draw_component['CenterX']) + float(draw_component['Radius'])

                    draw_component['StartY'] = float(draw_component['CenterY'])
                    draw_component['EndY'] = float(draw_component['CenterY'])

                # Arc 추가 
                arc_list.append(Arc(draw_component))
        return line_list, arc_list
    
    def rotation(self, angle, center:Point=None, inplace=False) -> 'Polygon':
        if center is None: 
            center = self.center
                    
        if inplace:
            self.lines = [line.rotation(angle, center, inplace) for line in self.lines]
            self.arcs = [arc.rotation(angle, center, inplace) for arc in self.arcs]
            return self
        else:
            lines = [line.rotation(angle, center, inplace) for line in self.lines]
            arcs = [arc.rotation(angle, center, inplace) for arc in self.arcs]
            return Polygon([lines, arcs], self.p_resolution)
    
class Component:
    def __init__(self, data:dict, p_resolution:float = 0.05) -> None:
        
        if type(data) == dict: 
            self.part_number = int(data['PartNo'])
            self.name = data['Name']
            self.placed_layer = data['PlacedLayer'] # 'TOP' 'BOTTOM'
            self.center = Point(float(data['X']), float(data['Y'])) 
            self.angle = float(data['Angle'])
            self.ecad_angle = float(data['ECADAngle'])
            self.pin_num = int(data['Pin_Num'])
            self.height = float(data['Height']) if data['Height'] != None else None
            self.part_name = data['PartName']
            self.ecad_part_name = data['ECADPartName']
            self.package_name = data['PackageName']
            self.top_area = Polygon(data['CompArea_Top'], p_resolution).move(self.center.x, self.center.y)
            self.bottom_area = Polygon(data['CompArea_Bottom'], p_resolution).move(self.center.x, self.center.y)
            self.top_prohibit_area = Polygon(data['CompProhibitArea_Top'], p_resolution).move(self.center.x, self.center.y)
            self.bottom_prohibit_area = Polygon(data['CompProhibitArea_Bottom'], p_resolution).move(self.center.x, self.center.y)
            self.hole_area = Polygon(data['HoleArea'], p_resolution).move(self.center.x, self.center.y)
            self.pin_dict = data['PinDict']
            self.fixed = data['Fixed']
            self.group = data['Group']
        else:
            NotImplementedError

        self.p_resolution = p_resolution

        # Component 초기화 
        self.initialize()
        
    def initialize(self) -> None:
        # unfixed component 에 대한 처리
        if self.fixed == False: 
            ## Center 0으로 초기화 
            # self.move_to(Point(0, 0), inplace=True)
            
            ## placed layer에 따라 스위칭
            if self.placed_layer == 'BOTTOM': 
                self.switch_layer()
                
            ## angle을 0으로 초기화
            self.rotation(-self.angle, inplace=True)
            
    def switch_layer(self) -> None:
        self.placed_layer = 'TOP' if self.placed_layer == 'BOTTOM' else 'BOTTOM'
        self.top_area, self.bottom_area = self.bottom_area, self.top_area
        self.top_prohibit_area, self.bottom_prohibit_area = self.bottom_prohibit_area, self.top_prohibit_area

        # self.cv_img가 그려져 있지 않을 경우가 존재 
        if hasattr(self, 'cv_top_img'):
            self.cv_top_img, self.cv_bottom_img = self.cv_bottom_img, self.cv_top_img

    def draw_cv(self, fill='in') -> tuple[np.array, np.array]:
        """
        - Desc -
            Component의 Pixel 이미지를 그리는 Method.
            그림은 placed layer 가 TOP 인 경우, Rotation이 0일 때, self.p_resolution 를 하나의 Pixel 단위로 그리고 부품명으로 저장
            만약 이미지가 존재할 경우 이미지를 불러오고 placed layer 에 맞춰서 Top 과 Bottom 이미지를 변환 
            
        ### 저장할 때 회전과 placed layer 고려해서 저장하고 불러올것 ... ###
            
        - Input -
            fill: 'in' or 'out'
        
        - Output -
            (cv_top_img, cv_bottom_img): top layer와 Bottom layer의 이미지
        
        """
        
        # path 관련 변수 설정 
        img_folder_ = os.path.join(img_folder, str(self.p_resolution))
        img_path = os.path.join(img_folder_, f'{self.name}.npy')
        
        if os.path.isfile(img_path):
            total_img = np.load(img_path)
            if len(total_img) != 2:
                raise Exception("The first dimension of img array must be 2.")
        else:
            # 좌측하단 원점으로 이동 
            total_area = self.top_area + self.bottom_area
            to_move_min_x, to_move_min_y = total_area.min_x, total_area.min_y 
            
            top_area = self.top_area.move(-to_move_min_x, -to_move_min_y)
            bottom_area = self.bottom_area.move(-to_move_min_x, -to_move_min_y)
            
            # Canvas 크기 계산 
            total_h = int(round(total_area.h / self.p_resolution, 0)) + 1
            total_w = int(round(total_area.w / self.p_resolution, 0)) + 1
            
            # Canvas 생성
            total_img = np.ones((2, total_h, total_w)) * 255
            total_img = total_img.astype(np.uint8)

            # top image 삽입 
            top_img = top_area.draw_cv(fill=fill, fitting=False)
            if top_img is not None: 
                total_img[0, total_img.shape[1] - top_img.shape[0]:, 0:top_img.shape[1]] = top_img 

            # bottom image 삽입 
            bottom_img = bottom_area.draw_cv(fill=fill, fitting=False)
            if bottom_img is not None: 
                total_img[1, total_img.shape[1] - bottom_img.shape[0]:, 0:bottom_img.shape[1]] = bottom_img 
                
            os.makedirs(img_folder_, exist_ok=True)
            
            np.save(img_path, total_img)

        self.cv_top_img = total_img[0, :, :]    
        self.cv_bottom_img = total_img[1, :, :]   
            
        return self.cv_top_img, self.cv_bottom_img     
        
    def draw_mat(self, ax, layer, shift_x=0, shift_y=0, color='k'): 
        if layer == 'TOP':
            self.top_area.draw_mat(ax, shift_x=shift_x, shift_y=shift_y, color=color)
        elif layer == 'BOTTOM':
            self.bottom_area.draw_mat(ax, shift_x=shift_x, shift_y=shift_y, color=color)
        self.hole_area.draw_mat(ax, shift_x=shift_x, shift_y=shift_y, color=color)

    def move(self, x, y, inplace=False):
        if inplace:
            self.top_area.move(x, y, inplace)
            self.bottom_area.move(x, y, inplace)
            self.hole_area.move(x, y, inplace)
            self.top_prohibit_area.move(x, y, inplace)
            self.bottom_prohibit_area.move(x, y, inplace)
            self.center.move(x, y, inplace)
            return self
        else:
            new_component = copy.deepcopy(self)
            return new_component.move(x, y, inplace=True)
        
    def move_to(self, point:Point, inplace:bool=False) -> 'Component':
        if inplace:
            self.move(point.x - self.center.x, point.y - self.center.y, inplace)
            return self
        else:
            new_component = copy.deepcopy(self)
            return new_component.move_to(point, inplace=True)
    
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
        
        # 이미지가 생성 안되어 있으면 새로 그리는 것 .. 
        # if 'self.cv_top_img' not in locals():
        #     self.cv_top_img, self.cv_bottom_img = self.draw_cv(fill)
        
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

    def rotation(self, angle, inplace=False):
        if inplace:
            # Attibutes 변경 
            self.angle += angle
            self.top_area.rotation(angle, self.center, inplace=True)
            self.bottom_area.rotation(angle, self.center, inplace=True)
            self.hole_area.rotation(angle, self.center, inplace=True)
            self.top_prohibit_area.rotation(angle, self.center, inplace=True)
            self.bottom_prohibit_area.rotation(angle, self.center, inplace=True) 
            
            # 이미지 회전
            k = angle // 90
            
            if 'cv_top_img' in dir(self):
                self.cv_top_img = img_rot_90(self.cv_top_img, k)
            if 'cv_bottom_img' in dir(self):
                self.cv_bottom_img = img_rot_90(self.cv_bottom_img, k)
            return self
        else:
            new_comp = copy.deepcopy(self)
            return new_comp.rotation(angle, inplace=True)
         