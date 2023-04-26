import pcb_parser
from pcb_parser import PCB
import os 
import json
import cv2 
import matplotlib.pyplot as plt  

os.chdir(os.path.abspath(os.path.dirname(__file__)))

with open("../data/debug_data.json", 'r') as f:
    data = json.load(f)

# Component 테스트
## PCB 객체 생성     
pcb = PCB(data)

figsize = (10, 10)
dpi = 300 
 
## Component 객체의 draw_cv 테스트 
component_name = 'C01B'
comp = pcb.components_dict[component_name]
top_img, bottom_img = comp.draw_cv(fill='in') 

## Component 객체의 Rotation 테스트 
comp_rot = comp.rotation(90)
top_rot_img, bottom_rot_img = comp_rot.cv_top_img, comp_rot.cv_bottom_img
cv2.imshow('TOP image', top_img)
# cv2.imshow('BOTTOM image', bottom_img)
cv2.imshow('TOP rot image', top_rot_img)
# cv2.imshow('BOTTOM rot image', bottom_rot_img)
cv2.waitKey(0) 
cv2.destroyAllWindows()

## Component의 draw_mat 테스트 
## Component 별로 TOP, BOTTOM 그림 그리기 
for component_name, v in pcb.components_dict.items():
    print(component_name, len(v.top_area), len(v.bottom_area))

    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111)
    # ax.xaxis.set_visible(False)
    # ax.yaxis.set_visible(False)

    comp = pcb.components_dict[component_name]
    comp.draw_mat(ax, layer='TOP')

    min_x, max_x, min_y, max_y = comp.get_size
    margin = 5
    
    ax.set_xlim([min_x-margin, max_x+margin])
    ax.set_ylim([min_y-margin, max_y+margin])
    ax.set_aspect('equal') #, 'box')
    plt.savefig(dpi=dpi, fname=f'./comp/{comp.name}_TOP.png')

    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111)
    # ax.xaxis.set_visible(False)
    # ax.yaxis.set_visible(False)

    comp.draw_mat(ax, layer='BOTTOM')

    # min_x, max_x, min_y, max_y = pcb.get_pcb_size
    ax.set_xlim([min_x-margin, max_x+margin])
    ax.set_ylim([min_y-margin, max_y+margin])
    ax.set_aspect('equal') #, 'box')
    plt.savefig(dpi=dpi, fname=f'./comp/{comp.name}_BOTTOM.png')
 


