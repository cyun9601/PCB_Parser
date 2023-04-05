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

with open("../data/debug_data.json", 'r') as f:
    data = json.load(f)

# PCB 테스트 
## PCB 객체 생성     
pcb = PCB(data, p_resolution = 0.05)

## Fixed Component 이미지를 Background에 합치기 
fixed_comp_name_list = pcb.get_fixed_components()
for fixed_comp_name in fixed_comp_name_list:
    collision = pcb.merge_component(fixed_comp_name, inplace=True)
print(pcb.state[0].shape)
    
## Unfixed Component 이미지를 Background에 합치기
unfixed_comp_name_list = pcb.get_unfixed_components()
for unfixed_comp_name in unfixed_comp_name_list:
    ## 모델 예측 -> 각 부품별 픽셀 위치 / 회전 
    
    ## Unfixed Component 의 위치 이동 
    pix_x = int(round(pcb.state[0].shape[0] / 2))
    pix_y = int(round(pcb.state[0].shape[1] / 2))
    pcb.move_to_pix(unfixed_comp_name, pix_x, pix_y)
    
    ## Unfixed Component 의 회전
    angle = 90
    pcb.rotation(unfixed_comp_name, angle)

    collision = pcb.merge_component(unfixed_comp_name, inplace=True)

# comp = pcb.components_dict[component_name]
# top, bottom = comp.draw_cv()
# front, back = comp.get_cv_img_center(size = board_img.shape, fill = False)

# comp_merge_img, collision = merge_polygon(merged_img, pcb.board, comp.top_area.move(0, 0, inplace = True), resolution=0.05)


# cv2.imshow('Board image', board_img)
# cv2.imshow('Hole', hole_img)
cv2.imshow('pcb top state', pcb.state[0])
cv2.imshow('pcb bottom state', pcb.state[1])

# cv2.imshow('t', top)
# cv2.imshow('b', bottom)
# cv2.imshow('comp_top', comp_top)
# cv2.imshow('comp_bottom', comp_bottom)
# cv2.imshow('comp_merge_img', comp_merge_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

## draw_mat test 
pcb.draw_mat('./pcb_top.png', layer='TOP')
pcb.draw_mat('./pcb_bottom.png', layer='BOTTOM')
pcb.draw_mat('./pcb_fixed_top.png', layer='TOP', only_fixed=True)
pcb.draw_mat('./pcb_fixed_bottom.png', layer='BOTTOM', only_fixed=True)
pcb.draw_mat('./pcb_fixed_bottom_red.png', layer='BOTTOM', only_fixed=True, color = 'red')