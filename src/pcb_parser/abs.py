from abc import *
from matplotlib.patches import Arc as mpl_Arc
from matplotlib.lines import Line2D
import os 
import copy 

class Object():
    
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
        # min_x, max_x, min_y, max_y
        ...
    
    @abstractmethod
    def w(self):
        ... 
        
    @abstractmethod
    def h(self):
        ... 
        
    @abstractmethod
    def draw_mat(self):
        ...
        
    @abstractmethod
    def move(self): 
        ...
        
    @abstractmethod 
    def move_to(self):
        ... 
        
    @abstractmethod 
    def center(self):
        ...
        
    def copy(self):
        return copy.deepcopy(self)