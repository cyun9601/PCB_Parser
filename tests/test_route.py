# %%
import sys 
# sys.path.append('/VOLUME/PNR/hjwon/PCB_Parser/src/')

from pcb_parser.geometry import Point, Line, Arc, Polygon, Component
from pcb_parser.parser import PCB
from pcb_parser.route import Router

import os 
import json
import cv2 
import matplotlib.pyplot as plt  
import random 

# %%
os.chdir(os.path.abspath(os.path.dirname(__file__)))

with open("/VOLUME/PNR/data/sample_data.json", 'r') as f:
    data = json.load(f)

pcb = PCB(data)

# %%
# Placement 
test_components = ['C01A', 'C01B', 'C01C', 'C01D', 'C01W']
to_delete = set(pcb.components_dict.keys()) - set(test_components)

for key in to_delete:
    del pcb.components_dict[key]
    
# %% 
comp_list = list(pcb.components_dict.keys())

for comp_name in comp_list:
    height, width = pcb.state[0].shape
    x, y = random.randint(1, width), random.randint(1, height)

    collision = pcb.put_component(comp_name, x, y)
    comp = pcb.get_component(comp_name)
    print(comp.name, f'{x}, {y}', f'{comp.min_x}, {comp.min_y}, {comp.center}', collision)
    
# cv2.imshow('Image', pcb.state[0])
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# %% 
# Routing 
router = Router(pcb)
router.pcb.net_list


a = 1