import pcb_parser
from pcb_parser import PCB
import os 
import json
import cv2 
import matplotlib.pyplot as plt  

os.chdir(os.path.abspath(os.path.dirname(__file__)))

with open("../data/sample_data.json", 'r') as f:
    data = json.load(f)

## PCB 객체 생성     
pcb = PCB(data)

## Draw method Test 
pcb.draw('./pcb_top.png', layer='TOP')
pcb.draw('./pcb_bottom.png', layer='BOTTOM')
pcb.draw('./pcb_fixed_top.png', layer='TOP', only_fixed=True)
pcb.draw('./pcb_fixed_bottom.png', layer='BOTTOM', only_fixed=True)
pcb.draw('./pcb_fixed_bottom_red.png', layer='BOTTOM', only_fixed=True, color = 'red')

figsize = (10, 10)
dpi = 300 

for component_name, v in pcb.components_dict.items():
    print(component_name, len(v.top_area), len(v.bottom_area))

    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111)
    # ax.xaxis.set_visible(False)
    # ax.yaxis.set_visible(False)

    comp = pcb.components_dict[component_name]
    comp.draw(ax, layer='TOP')

    min_x, max_x, min_y, max_y = comp.get_size
    margin = 5
    
    ax.set_xlim([min_x-margin, max_x+margin])
    ax.set_ylim([min_y-margin, max_y+margin])
    ax.set_aspect('equal') #, 'box')
    plt.savefig(dpi=dpi, fname=f'./comp/{comp.part_name}_TOP.png')


    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111)
    # ax.xaxis.set_visible(False)
    # ax.yaxis.set_visible(False)

    comp.draw(ax, layer='BOTTOM')

    # min_x, max_x, min_y, max_y = pcb.get_pcb_size
    ax.set_xlim([min_x-margin, max_x+margin])
    ax.set_ylim([min_y-margin, max_y+margin])
    ax.set_aspect('equal') #, 'box')
    plt.savefig(dpi=dpi, fname=f'./comp/{comp.part_name}_BOTTOM.png')

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