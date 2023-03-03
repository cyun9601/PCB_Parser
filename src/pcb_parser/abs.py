from abc import *
from matplotlib.patches import Arc as mpl_Arc
from matplotlib.lines import Line2D
import os 

class Draw_type(metaclass = ABCMeta):
    @abstractmethod
    def draw(self):
        ...