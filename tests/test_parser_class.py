import pcb_parser
from pcb_parser import PCB
import os 
import json
import cv2 
 
os.chdir(os.path.abspath(os.path.dirname(__file__)))

with open("../data/sample_data.json", 'r') as f:
    data = json.load(f)
    
pcb = PCB(data)

pcb.draw('./pcb_top.png', layer='TOP')
pcb.draw('./pcb_bottom.png', layer='BOTTOM')
pcb.draw('./pcb_fixed_top.png', layer='TOP', only_fixed=True)
pcb.draw('./pcb_fixed_bottom.png', layer='BOTTOM', only_fixed=True)
pcb.draw('./pcb_fixed_bottom_red.png', layer='BOTTOM', only_fixed=True, color = 'red')
