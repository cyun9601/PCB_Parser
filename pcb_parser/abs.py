from abc import *
from matplotlib.patches import Arc as mpl_Arc
from matplotlib.lines import Line2D
import os 

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
