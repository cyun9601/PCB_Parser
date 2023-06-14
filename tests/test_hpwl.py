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
pcb.get_hpwl()