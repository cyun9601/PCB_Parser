from shapely.geometry import Polygon, MultiLineString
from shapely.plotting import plot_polygon, plot_points # , plot_line
import matplotlib.pyplot as plt
from dtypes import Shape, PCB, Arc, Line
import json
from matplotlib.patches import Arc as m_Arc
from matplotlib.lines import Line2D

def plot_line(lines: list[Line], ax, shift=None):
    for line in lines:
        if shift is not None:
            l = Line2D(*line.move(shift))
        else:
            l = Line2D(*line.get_line())
        ax.add_line(l)

def plot_arc(arcs:list[Arc], ax, shift=None):
    for arc in arcs: 
        if shift is not None: 
            center = arc.move(shift)
        else : 
            center = arc.get_center()
        width = arc.radius * 2
        height = arc.radius * 2
        angle = 0
        if arc.direction == 'CW': 
            theta1 = arc.eAngle
            theta2 = arc.sAngle
        elif arc.direction == 'CCW':
            theta1 = arc.sAngle
            theta2 = arc.eAngle
            
        ax.add_patch(m_Arc(center, width, height, angle, theta1, theta2))

def draw_shape(comp, ax, shift=None):
    ## line plot 
    # multi_lines = MultiLineString([line.get_line for line in comp.lines])
    # plot_line(multi_lines, ax=ax)
    plot_line(comp.lines, ax, shift)

    ## arc plot
    plot_arc(comp.arcs, ax, shift)

def draw_component(component_dict:dict, ax):
    for component in component_dict.values():
        draw_shape(component.component_top_shape, ax, (component.x, component.y))

def show(board:Shape, hole_area:Shape, component_dict:dict, net_list:dict):
    fig = plt.figure(1, figsize=(10, 10), dpi=90)

    ax = fig.add_subplot(111)

    ## draw board
    draw_shape(board, ax)
    
    ## draw hole area 
    draw_shape(hole_area, ax)
    
    ## draw component_dict 
    draw_component(component_dict, ax)
    # draw_shape(list(component_dict.values())[0].component_top_shape, ax, (list(component_dict.values())[0].x, list(component_dict.values())[0].y))
    # draw_shape(component_dict, ax)
    
    # ax.add_patch(arc)
    ax.set_title('a) valid')
    # 축의 범위 설정
    ax.set_xlim([0, 60])
    ax.set_ylim([0, 150])
    ax.set_aspect('equal') #, 'box')
    
    plt.savefig(dpi=300, fname='shapely_polygon.png')

     
    
if __name__=="__main__": 

    with open("./data/sample_data.json", 'r') as f:
            data = json.load(f)

    pcb = PCB(list(data.values())[0])

    show(pcb.board, pcb.hole_area, pcb.component_dict, pcb.net_list)
    

    