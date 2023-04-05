import json 
from abc import *
import matplotlib.pyplot as plt
from .geometry import Component, Polygon, Line, Arc, Point
from tqdm.auto import tqdm 
import numpy as np
import copy 

class Net: # dataclass 
    def __init__(self, net_info:dict) -> None:
        self.placed_layer = net_info['PlacedLayer']
        self.name = net_info['Name']
        self.pin_no = net_info['PinNo']

class PCB:
    def __init__(self, pcb_dict:json, p_resolution:float=0.05) -> None:
        self.p_resolution = p_resolution
        self.pcb_info = list(pcb_dict.values())[0]
        self.file_name = self.pcb_info['FileName']
        self.file_format = self.pcb_info['FileFormat']
        self.board = Polygon(self.pcb_info['BOARD_FIGURE'], p_resolution)
        self.hole_area = Polygon(self.pcb_info['HoleArea'], p_resolution)
        self.prohibit_area = Polygon(self.pcb_info['ProhibitArea'], p_resolution)
        self.components_dict = {comp_info['Name']:Component(comp_info, p_resolution) for comp_info in self.pcb_info['ComponentDict'].values()}
        self.net_list = dict(zip(self.pcb_info['NetDict'].keys(), [Net(net_info) for net_info in list(self.pcb_info['NetDict'].values())]))
        
        # 초기화 
        self.initialize_cv_img()
        self.initialize_background()
    
    def initialize_cv_img(self):
        # initialize
        print('Board 이미지 생성 중...')
        self.board.draw_cv()
        self.hole_area.draw_cv()
        self.prohibit_area.draw_cv()         
        print('Component 이미지 생성 중...')
        pbar = tqdm(self.components_dict.values())
        for comp in pbar:
            pbar.set_description(comp.name)
            comp.draw_cv()
    
    def initialize_background(self):
        board_cv_img = self.board.draw_cv(fill='out')

        merged_img, collision = self.merge_polygon(board_cv_img, self.board, self.hole_area, inplace=False)
        self.state = [copy.deepcopy(merged_img), copy.deepcopy(merged_img)]
        
    def get_fixed_components(self) -> list[str]:
        return [comp.name for comp in self.components_dict.values() if comp.fixed]
    
    def get_unfixed_components(self) -> list[str]:
        return [comp.name for comp in self.components_dict.values() if not comp.fixed]
    
    def move_to_pix(self, component_name, pix_x:int, pix_y:int): 
        to_x = pix_x * self.p_resolution
        to_y = pix_y * self.p_resolution
        self.components_dict[component_name].move_to(Point(to_x, to_y), inplace=True)
    
    def rotation(self, component_name, angle):
        self.components_dict[component_name].rotation(angle, inplace=True)
    
    def get_component_img(self, component_name:str, img_size:tuple, fill=True):
        comp = self.components_dict[component_name]
        return comp.get_cv_img_center(size = img_size, fill = fill)
    
    def switch_component_layer(self, component_name:str):
        self.components_dict[component_name].switch_layer()
    
    def draw_mat(self, image_name:str, layer:str, only_fixed:bool=False, shift_x=0, shift_y=0, save=True, figsize=(10, 10), color='k', dpi:int=300) -> dict:
        fig = plt.figure(figsize=figsize, dpi=dpi)
        ax = fig.add_subplot(111)
        
        self.board.draw_mat(ax, shift_x=shift_x, shift_y=shift_y, color=color)
        self.hole_area.draw_mat(ax, shift_x=shift_x, shift_y=shift_y, color=color)
        
        # draw components
        for _, v in self.components_dict.items():
            # if v.placed_layer == layer and (not only_fixed or v.fixed):
            v.draw_mat(ax, layer, shift_x=shift_x, shift_y=shift_y, color=color)
        
        # ax.set_title('a) valid')
        min_x, max_x, min_y, max_y = self.get_size
        ax.set_xlim([min_x, max_x])
        ax.set_ylim([min_y, max_y])
        ax.set_aspect('equal') #, 'box')
        
        if save:
            plt.savefig(dpi=dpi, fname=image_name)
        return fig, ax
    
    #def draw_cv(self):
        '''
        *args : 부품이름 layer
        '''
     #   return   
        
    @property
    def get_size(self):
        return self.board.bounding_box
    
    def get_component(self, name:str):
        return self.components_dict[name]
    
    def merge_polygon(self, base_img:np.array, background:Polygon, foreground:Polygon, inplace = False) -> tuple[np.array, bool]:
        collision = False
        
        # foreground의 Polygon이 존재하지 않을 경우 예외처리 
        if len(foreground) == 0:
            return base_img, collision
        
        if inplace == False:
            base_img = copy.deepcopy(base_img)
        
        back_pix_h = int(round(background.h / self.p_resolution, 0)) + 1
        back_pix_w = int(round(background.w / self.p_resolution, 0)) + 1
        
        ## Component의 원점 매핑 시 BBox 계산. 
        moved_min_x = foreground.min_x - background.min_x
        moved_max_x = foreground.max_x - background.min_x
        moved_min_y = foreground.min_y - background.min_y 
        moved_max_y = foreground.max_y - background.min_y 

        ## Pixel 영역에서의 BBox 영역 매핑 
        min_pix_h = back_pix_h - 1 - int(round((moved_max_y / self.p_resolution), 0))
        max_pix_h = back_pix_h - 1 - int(round((moved_min_y / self.p_resolution), 0))
        min_pix_w = int(round((moved_min_x / self.p_resolution), 0))
        max_pix_w = int(round((moved_max_x / self.p_resolution), 0))

        ## 이미지 범위 검사 
        if (min_pix_h < 0) or (min_pix_w < 0) or (max_pix_h > back_pix_h) or (max_pix_w > back_pix_w):
            return base_img, True

        ## 이미지 삽입 
        partial_base_img = base_img[min_pix_h:min_pix_h+foreground.cv_img.shape[0], min_pix_w:min_pix_w+foreground.cv_img.shape[1]]
        if ((partial_base_img == 0) & (foreground.cv_img == 0)).sum() > 0: 
            collision = True
        else: 
            base_img[min_pix_h:min_pix_h+foreground.cv_img.shape[0], min_pix_w:min_pix_w+foreground.cv_img.shape[1]] = foreground.cv_img 
        return base_img, collision
    
    def merge_component(self, component_name:str, inplace=True) -> list[bool]:
        collision = [False, False]
        comp = self.get_component(component_name)
        polyg = [comp.top_area, comp.bottom_area]
        
        for i in range(2):
            self.state[i], collision[i] = self.merge_polygon(self.state[i], self.board, polyg[i], inplace=inplace)
        return collision