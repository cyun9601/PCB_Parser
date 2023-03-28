import pcb_parser
from pcb_parser import PCB
import os 
import json
import cv2 
import matplotlib.pyplot as plt  

os.chdir(os.path.abspath(os.path.dirname(__file__)))

with open("../data/sample_data.json", 'r') as f:
    data = json.load(f)

# PCB 테스트 
## PCB 객체 생성     
pcb = PCB(data)

## Draw method Test 
pcb.draw_mat('./pcb_top.png', layer='TOP')
pcb.draw_mat('./pcb_bottom.png', layer='BOTTOM')
pcb.draw_mat('./pcb_fixed_top.png', layer='TOP', only_fixed=True)
pcb.draw_mat('./pcb_fixed_bottom.png', layer='BOTTOM', only_fixed=True)
pcb.draw_mat('./pcb_fixed_bottom_red.png', layer='BOTTOM', only_fixed=True, color = 'red')