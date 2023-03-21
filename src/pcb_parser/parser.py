import json 
from abc import *
import matplotlib.pyplot as plt
from .geometry import Component, Poligon

class Net: # dataclass 
    def __init__(self, net_info:dict) -> None:
        self.placed_layer = net_info['PlacedLayer']
        self.name = net_info['Name']
        self.pin_no = net_info['PinNo']

class PCB:
    def __init__(self, pcb_dict:json) -> None:
        self.pcb_info = list(pcb_dict.values())[0]
        self.file_name = self.pcb_info['FileName']
        self.file_format = self.pcb_info['FileFormat']
        self.board = Poligon(self.pcb_info['BOARD_FIGURE']) 
        self.hole_area = Poligon(self.pcb_info['HoleArea'])
        self.prohibit_area = Poligon(self.pcb_info['ProhibitArea'])
        self.components_dict = {comp_info['PartName']:Component(comp_info) for comp_info in self.pcb_info['ComponentDict'].values()}
        self.net_list = dict(zip(self.pcb_info['NetDict'].keys(), [Net(net_info) for net_info in list(self.pcb_info['NetDict'].values())]))
    
    def draw(self, image_name:str, layer:str, only_fixed:bool=False, shift=None, save=True, figsize=(10, 10), color='k', dpi:int=300) -> dict:
        fig = plt.figure(figsize=figsize, dpi=dpi)
        ax = fig.add_subplot(111)
        
        self.board.draw(ax, shift=shift, color=color)
        self.hole_area.draw(ax, shift=shift, color=color)
        
        # draw components
        for _, v in self.components_dict.items():
            if v.placed_layer == layer and (not only_fixed or v.fixed):
                v.draw(ax, shift=shift, color=color)
        
        # ax.set_title('a) valid')
        min_x, max_x, min_y, max_y = self.get_pcb_size
        ax.set_xlim([min_x, max_x])
        ax.set_ylim([min_y, max_y])
        ax.set_aspect('equal') #, 'box')
        
        if save: 
            plt.savefig(dpi=dpi, fname=image_name)
        return fig, ax
    
    @property 
    def get_pcb_size(self):
        return self.board.bounding_box
    
    def find_component(self, part_name:str):
        return NotImplementedError