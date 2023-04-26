#%%
import sys 
sys.path.append('/VOLUME/PNR/hjwon/PCB_Parser/src/')

from pcb_parser.geometry import Point, Line, Arc, Polygon, Component
import os 
import json
import cv2 
import matplotlib.pyplot as plt  
import numpy as np 

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


##
# Arc 
## 객체 생성 
p1 = Point(1, 0)
p2 = Point(0, 1)

arc1 = Arc([p1, p2], radius=1, sAngle=0, eAngle=90, direction='CCW', centerX=0, centerY=0)
print("arc1: ", arc1)

arc2 = arc1.move(10, 20)
print("arc2: ", arc2)
print("arc2: ", arc2.center)

arc3 = Arc(
            [Point(4.663, -0.35), Point(3.3366, -0.350)], 
            radius = 0.75, 
            sAngle = 332.18, 
            eAngle = 207.81, direction = 'CCW', centerX = 4, centerY = 0)

arc4 = Arc(
            [Point(4.663, -0.35), Point(3.3366, -0.350)], 
            radius = 0.75, 
            sAngle = 207.81, 
            eAngle = 332.18, direction = 'CW', centerX = 4, centerY = 0)

arc5 = Arc(
            [Point(4.75, 0), Point(4.75, 0)], 
            radius = 0.75, 
            sAngle = 0, 
            eAngle = 360, direction = 'CW', centerX = 4, centerY = 0)

points = arc3.ext_points()
arc_x_list = [t.x for t in points]
arc_y_list = [t.y for t in points]

figsize = (10, 10)
dpi = 300 
fig = plt.figure(figsize=figsize, dpi=dpi)
ax = fig.add_subplot(111)
ax.set_aspect('equal') #, 'box')
arc3.draw_mat(ax)

plt.plot(arc_x_list, arc_y_list, 'r')
plt.xlim([0, 10])
plt.ylim([-5, 5])
plt.savefig(dpi=dpi, fname='arc3_debug.png')


points = arc4.ext_points()
arc_x_list = [t.x for t in points]
arc_y_list = [t.y for t in points]

figsize = (10, 10)
dpi = 300 
fig = plt.figure(figsize=figsize, dpi=dpi)
ax = fig.add_subplot(111)
ax.set_aspect('equal') #, 'box')
arc3.draw_mat(ax)

plt.plot(arc_x_list, arc_y_list, 'r')
plt.xlim([0, 10])
plt.ylim([-5, 5])
plt.savefig(dpi=dpi, fname='arc4_debug.png')

## bounding box test
min_x, max_x, min_y, max_y = arc1.bounding_box
print("arc1 bbox: ", min_x, max_x, min_y, max_y)

min_x, max_x, min_y, max_y = arc2.bounding_box
print("arc2 bbox: ", min_x, max_x, min_y, max_y)

min_x, max_x, min_y, max_y = arc3.bounding_box
print("arc3 bbox: ", min_x, max_x, min_y, max_y)

min_x, max_x, min_y, max_y = arc4.bounding_box
print("arc4 bbox: ", min_x, max_x, min_y, max_y)

min_x, max_x, min_y, max_y = arc5.bounding_box
print("arc5 bbox: ", min_x, max_x, min_y, max_y)


# Polygon
## 객체 생성
lines = [l1, l2, l3]
arcs = [] 
polygon = Polygon([lines, arcs])

## draw_cv test 
cv_img = polygon.draw_cv()
cv2.imshow('Color image', cv_img)
cv2.waitKey(0)
cv2.destroyAllWindows()