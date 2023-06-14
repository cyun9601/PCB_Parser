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

# 009mo%%
A = Point(3.5, 4.5) 
B = Point(7.5, -3.5)
