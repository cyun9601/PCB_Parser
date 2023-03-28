from pcb_parser.geometry import Point, Line, Arc, Polygon, Component
import os 
import json
import cv2 
import matplotlib.pyplot as plt  
import numpy as np 

os.chdir(os.path.abspath(os.path.dirname(__file__)))

with open("../data/sample_data.json", 'r') as f:
    data = json.load(f)

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
p1 = Point(1, 2)
p2 = Point(3, 3)
p3 = Point(2, 1)

l1 = Line([p1, p2])
l2 = Line([p2, p3])
l3 = Line([p3, p1])
print("l1: ", l1)
print("l2: ", l2)
print("l3: ", l3)

## Line 이동 
moved = l1.move(10.5, -10, inplace = False)
print("moved: ", moved)

l1.move(10.5, -10) # inplace = True)
print("l1: ", l1)

# Arc 
## 객체 생성 
p1 = Point(1, 0)
p2 = Point(0, 1)

arc1 = Arc([p1, p2], radius=1, sAngle=0, eAngle=90, direction='CCW', centerX=0, centerY=0)
print("arc1: ", arc1)

arc2 = arc1.move(10, 20)
print("arc2: ", arc2)
print("arc2: ", arc2.center)

# Polygon
## 객체 생성
lines = [l1, l2, l3]
arcs = [] 
polygon = Polygon([lines, arcs])

## draw_cv test 
cv_img = polygon.draw_cv(resolution=0.05)
cv2.imshow('Color image', cv_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

'''
## Flood fill test
component_name = 'SAA35069001-BF-MICOM'
figsize = (pcb.components_dict[component_name].w * 0.0393701, pcb.components_dict[component_name].h * 0.0393701)
# figsize = (10, 10)
dpi = 300 

fig = plt.figure(figsize=figsize, dpi=dpi)
ax = fig.add_subplot(111)
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)

pcb.components_dict[component_name].draw(ax)

# ax.set_title('a) valid')
min_x, max_x, min_y, max_y = pcb.get_pcb_size
ax.set_xlim([min_x, max_x])
ax.set_ylim([min_y, max_y])
ax.set_aspect('equal') #, 'box')
plt.savefig(dpi=dpi, fname='result.png')
'''