from pcb_parser.geometry import Point, Line, Arc, Polygon, Component
import os 
import json
import cv2 
import matplotlib.pyplot as plt  

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
p1 = Point(10, 20)
p2 = Point(30, 50)

l1 = Line([p1, p2])
print("l1: ", l1)

## Line 이동 
moved = l1.move(10.5, -10, inplace = False)
print("moved: ", moved)

l1.move(10.5, -10, inplace = True)
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

