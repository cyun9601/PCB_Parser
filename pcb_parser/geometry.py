from abc import *
from matplotlib.patches import Arc as mpl_Arc
from matplotlib.lines import Line2D
import os 
from abs import Geometry, Draw_type

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
            

if __name__=="__main__": 

    os.chdir(os.path.abspath(os.path.dirname(__file__)))
