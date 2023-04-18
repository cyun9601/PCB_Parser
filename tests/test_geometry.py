#%%
import sys 
sys.path.append('/VOLUME/PNR/hjwon/PCB_Parser/src/')

from pcb_parser.geometry import Point, Line, Arc, Polygon, Component
import os 
import json
import cv2 
import matplotlib.pyplot as plt 
import numpy as np 
from matplotlib import pyplot as plt
from matplotlib.patches import Arc as mpl_Arc
#%%
os.chdir(os.path.abspath(os.path.dirname(__file__)))

with open("/VOLUME/PNR/data/sample_data.json", 'r') as f:
    data = json.load(f)
#%%
# Point 
## 객체 생성 
p1 = Point(10, 20)
print("p1: ", p1)

## Point Method 
moved = p1.move(20, 30, inplace = False)
print("moved: ", moved)

p1.move(20, 30, inplace = True)
print("p1: ", p1)

p2 = p1 + moved
print("p2: ", p2)

p3 = p2 / 3
print("p3: ", p3)

# Line 
## 객체 생성 
p1 = Point(10, 20)
p2 = Point(30, 50)

l1 = Line([p1, p2])
print("l1: ", l1)

## Line 이동 
moved = l1.move(10.5, -10, inplace = False)
print("moved: ", moved)

l1.move(10.5, -10, inplace = True)
print("l1: ", l1)

## Line cv draw 
arr = np.ones((100,100,3), dtype=np.uint8)*255  
arr = l1.draw_cv(arr)

##
#%%
# Arc 
## 객체 생성 
p1 = Point(1, 0)
p2 = Point(0, 1)

arc1 = Arc([p1, p2], radius=1, sAngle=0, eAngle=90, direction='CCW', centerX=0, centerY=0)
print("arc1: ", arc1)

arc2 = arc1.move(10, 20)
print("arc2: ", arc2)
print("arc2: ", arc2.center)

#%%
# %%
x = [i.x for i in arc1.ext_points()] #x축 좌표
y = [i.y for i in arc1.ext_points()] 
arc_min  = min(x),min(y)
arc_max  = max(x),max(y)

fig = plt.figure(figsize=(50,50), dpi=100)
ax = fig.add_subplot(111)

center = arc1.center
width = arc1.radius * 2
height = arc1.radius * 2
angle = 0
        
if arc1.direction == 'CW' or arc1.direction == None:
    theta1 = arc1.eAngle
    theta2 = arc1.sAngle
elif arc1.direction == 'CCW':
    theta1 = arc1.sAngle
    theta2 = arc1.eAngle
ax.add_patch(mpl_Arc(center.to_tuple(), width, height, angle, theta1, theta2, color='r'))
        
#if bbox:
min_x, min_y = arc_min 
max_x, max_y = arc_max
rect = plt.Rectangle((min_x, min_y), max_x-min_x, max_y-min_y, linewidth=5, edgecolor='b', facecolor='none')
ax.add_patch(rect)
# %%
