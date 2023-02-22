from shapely.geometry import Polygon, MultiLineString
from shapely.plotting import plot_polygon, plot_points # , plot_line
import matplotlib.pyplot as plt
from dtypes import Shape, PCB, Arc, Line
import json
from matplotlib.patches import Arc as m_Arc
from matplotlib.lines import Line2D
import os 

if __name__=="__main__": 

    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    with open("./data/sample_data.json", 'r') as f:
        data = json.load(f)

    pcb = PCB(list(data.values())[0])
    pcb.draw()
    