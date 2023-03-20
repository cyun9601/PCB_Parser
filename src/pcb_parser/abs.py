from abc import *
from matplotlib.patches import Arc as mpl_Arc
from matplotlib.lines import Line2D
import os 

class Draw_type(metaclass = ABCMeta):
    @abstractmethod
    def min_x(self):
        ... 
        
    @abstractmethod
    def max_x(self):
        ... 
        
    @abstractmethod
    def min_y(self):
        ... 
        
    @abstractmethod
    def max_y(self):
        ...
    
    @abstractmethod
    def bounding_box(self):
        ...
    
    @abstractmethod
    def w(self):
        ... 
        
    @abstractmethod
    def h(self):
        ... 
        
    @abstractmethod
    def draw(self):
        ...
        
    @abstractmethod 
    def translation(self, shift, inplace = False):
        ... 