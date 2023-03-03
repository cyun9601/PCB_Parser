from abc import *
from matplotlib.patches import Arc as mpl_Arc
from matplotlib.lines import Line2D
import os 
from .abs import Draw_type

class Geometry: # dataclass 
    def __init__(self, **kwargs) -> None:
        self.type = kwargs['type']
        self.startX = float(kwargs['StartX'])
        self.startY = float(kwargs['StartY'])
        self.endX = float(kwargs['EndX'])
        self.endY = float(kwargs['EndY'])
        if kwargs['Radius'] != None: self.radius = float(kwargs['Radius'])
        if kwargs['SAngle'] != None: self.sAngle = float(kwargs['SAngle'])
        if kwargs['EAngle'] != None: self.eAngle = float(kwargs['EAngle'])
        self.direction = kwargs['Direction'] if kwargs['Direction'] != None else None
        if kwargs['CenterX'] != None: self.centerX = float(kwargs['CenterX'])
        if kwargs['CenterY'] != None: self.centerY = float(kwargs['CenterY'])
        

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