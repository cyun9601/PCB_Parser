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
## 특정 Component와 연관이 있는 부품들의 목록을 추출
center_component = 'CN485_ANGLE'
connected_comp_list = pcb.get_connected_comps(center_component)

## 해당 목록에 존재하지 않는 Comp들 제거
to_delete = set(pcb.components_dict.keys()) - set(connected_comp_list)

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
router = Router(pcb, resolution=0.005)
for k, v in router.net.items():
    router.routing(wire_name=k, wire_num=1000)

comp = router.pcb.get_component(center_component)

# 특정 Component의 Pin 위치를 가져옴 
p = router.get_pin_position(comp_name, 1)