import pygame
import shapely.geometry as sg
import shapely.affinity as sa
import shapely.ops as so
from dtypes import Shape, PCB
import json

def show(board:Shape, hold_area:Shape, component_dict:dict, net_list:dict):
    pass
        
    
if __name__=="__main__": 

    with open("./data/sample_data.json", 'r') as f:
            data = json.load(f)

    pcb = PCB(list(data.values())[0])

    show(pcb.board, pcb.hole_area, pcb.component_dict, pcb.net_list)
    