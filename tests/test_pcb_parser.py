import pcb_parser
from pcb_parser import PCB
from pcb_parser.geometry import Polygon, Component, merge_polygon
import os 
import json
import cv2 
import matplotlib.pyplot as plt  
import numpy as np 
import copy 


os.chdir(os.path.abspath(os.path.dirname(__file__)))

with open("../data/sample_data.json", 'r') as f:
    data = json.load(f)

# PCB 테스트 
## PCB 객체 생성     
pcb = PCB(data)

## draw_cv test 
board_img = pcb.board.draw_cv(fill='out')
bb = pcb.hole_area.draw_cv(fill='in') # img = board_img)

rr, collision = merge_polygon(board_img, pcb.board, pcb.hole_area, resolution=0.05)
print("collision: ", collision)

component_name = '6630A90002C-BSBPBF-CN485_STRAIGHT'
comp = pcb.components_dict[component_name]
top, bottom = comp.draw_cv()
front, back = comp.get_cv_img_center(size = board_img.shape, fill = False)

# cv2.imshow('Board image', board_img)
# cv2.imshow('Hole', bb)
# cv2.imshow('sum', rr)
cv2.imshow('t', top)
cv2.imshow('b', bottom)
cv2.imshow('front', front)
cv2.imshow('back', back)
cv2.waitKey(0)
cv2.destroyAllWindows()

## draw_mat test 
pcb.draw_mat('./pcb_top.png', layer='TOP')
pcb.draw_mat('./pcb_bottom.png', layer='BOTTOM')
pcb.draw_mat('./pcb_fixed_top.png', layer='TOP', only_fixed=True)
pcb.draw_mat('./pcb_fixed_bottom.png', layer='BOTTOM', only_fixed=True)
pcb.draw_mat('./pcb_fixed_bottom_red.png', layer='BOTTOM', only_fixed=True, color = 'red')