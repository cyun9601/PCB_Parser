import json 
from abc import *
import matplotlib.pyplot as plt
from .geometry import Component, Polygon, Line, Arc, Point, BBox
from tqdm.auto import tqdm 
import numpy as np
import copy 


class Net: # dataclass 
    def __init__(self, net_info:dict) -> None:
        self.placed_layer = net_info['PlacedLayer']
        self.name = net_info['Name']
        self.pin_no = net_info['PinNo']

class PCB:
    def __init__(self, pcb_dict:json, resolution:float=0.05) -> None:
        self.pcb_info = list(pcb_dict.values())[0]
        self.__resolution = resolution
        self.file_name = self.pcb_info['FileName']
        self.file_format = self.pcb_info['FileFormat']
        self.__initialize()
    
    @property 
    def resolution(self):
        return self.__resolution
    
    def update_resolution(self, resolution:float):
        """
        - Description -
        PCB 객체의 Resolution 을 업데이트하면 Resolution 을 반영하여 모든 객체를 업데이트
        
        - Input - 
        resolution(float): 업데이트할 Resolution 값
         
        """
        self.__resolution = resolution
        self.__initialize()
        self.__initialize_cv_img()
        self.__initialize_background()
    
    def __initialize(self):
        """
        - Description -
        PCB 정보를 포함하는 self.pcb_info 에서 PCB 정보를 추출하고 CV 맵 및 Component 를 그려서 저장 
        
        self.__gen_object: self.pcb_info 의 Polygon, Component, Net 정보를 추출하여 객체 생성
        self.__initialize_cv_img: self.__gen_object 에서 생성된 객체들의 CV 이미지 생성
        self.__initialize_background: self.__initialize_cv_img 에서 생성된 이미지를 바탕으로 Top layer와 Bottom layer의 초기 이미지 생성
        """

        # Polygon, Component, Net list 객체 생성 
        self.__parsing_json()
        
        ## Comp 이미지 생성
        self.__initialize_cv_img()
    
        ## Background 초기화 -> self.state 생성 
        self.__initialize_background()
        
    def __parsing_json(self):
        """
        - Description - 
        PCB Dict 데이터를 Parsing 하여 Polygon, Component, Net 객체를 생성 
        """
        
        self.board = Polygon(self.pcb_info['BOARD_FIGURE'], self.__resolution)
        self.hole_area = Polygon(self.pcb_info['HoleArea'], self.__resolution)
        self.prohibit_area = Polygon(self.pcb_info['ProhibitArea'], self.__resolution)
        self.components_dict = {comp_info['Name']:Component(comp_info, self.__resolution) for comp_info in self.pcb_info['ComponentDict'].values()}
        self.net_list = dict(zip(self.pcb_info['NetDict'].keys(), [Net(net_info) for net_info in list(self.pcb_info['NetDict'].values())]))
        
    def __initialize_cv_img(self) -> None:
        """
        - Description - 
        Polygon, Component 객체들의 CV 이미지를 생성 
        """
        
        # initialize
        print('Board 이미지 생성 중...')
        self.board.draw_cv(fill='out')
        self.hole_area.draw_cv()
        self.prohibit_area.draw_cv()
        print('Component 이미지 생성 중...')
        pbar = tqdm(self.components_dict.values())
        for comp in pbar:
            pbar.set_description(comp.name)
            comp.draw_cv()
    
    def __initialize_background(self) -> None:
        """
        - Desc -
        PCB의 테두리와 Hole이 결합된 Background 이미지 (self.state) 를 생성
        """
        
        merged_img, collision = self.merge_polygon(self.board.cv_img, self.board, self.hole_area, inplace=False)
        self.state = [copy.deepcopy(merged_img), copy.deepcopy(merged_img)]
        
    def __initialize_components(self):
        """
        - Desc -
        self.components_dict 의 모든 Components 들을 초기화.
        """
        
        for comp in self.components_dict.values():
            comp.initialize()
        
    def get_obj_bounding_box(obj_list:list) -> BBox:
        """
        - Desc -
        obj_list 의 모든 Component 들의 Bounding Box 를 반환
        """
        bbox = obj_list[0].bounding_box
        if len(obj_list) == 1: 
            return bbox
        elif len(obj_list) >= 2:
            for obj in obj_list[1:]:
                bbox = bbox + obj.bounding_box
        return bbox
    
    def get_hpwl(self):
        """
        - Desc -
        self.net_list 의 모든 HPWL 을 반환
        """
        hpwl = 0 

        for net_name, net_list in self.net_list.items():
            comp_name_list, pin_no_list = net_list.name, net_list.pin_no
            
            pin_position_list = []
            for comp_name, pin_no in zip(comp_name_list, pin_no_list):
                pin_position = self.get_component(comp_name).get_pin_position(pin_no)
                pin_position_list.append(pin_position)
            
            bbox = self.get_obj_bounding_box(pin_position_list)
            
            hpwl = hpwl + bbox.width + bbox.height + 2
            
        return hpwl
        
    def reset(self):
        """
        - Desc -
        모든 Component 들을 초기화하고 Background 이미지를 생성하여 self.state 에 저장.
        """
        
        self.__initialize_components()
        self.__initialize_background()
        
    def get_fixed_components(self) -> list[str]:
        """
        - Desc -
        component의 fixed 가 True 인 Component 이름을 반환
        """
        return [comp.name for comp in self.components_dict.values() if comp.fixed]
    
    def get_unfixed_components(self) -> list[str]:
        return [comp.name for comp in self.components_dict.values() if not comp.fixed]
    
    def get_connected_wires(self, comp_name:str) -> list[str]:
        '''
        - Desc -
        comp_name과 연결 관계를 갖는 wire list 를 반환 
        comp -> wire
        
        - Input -
        comp_name(str): component name
        
        - Output -
        connected_wire_list(list): comp_name과 연결 관계를 갖는 wire list
        '''
        
        connected_wire_list = []
        
        for net_name, values in self.net_list.items():
            if comp_name in values.name:
                connected_wire_list.append(net_name)
        return connected_wire_list
    
    def get_connected_comps(self, comp_name:str) -> list[str]:
        '''
        - Desc -
        comp_name과 연결 관계를 갖는 comp list 를 반환
        comp -> comp
        
        - Input -
        comp_name(str): Component 이름 
        
        - Output -
        connected_comp_list(list): comp_name과 연결 관계를 갖는 comp list
        '''
        wires_list = self.get_connected_wires(comp_name)
        
        comp_list = []
        for wire in wires_list:
            comp_list.extend(self.net_list[wire].name)
        comp_list = list(set(comp_list))
        comp_list.remove(comp_name)
        return comp_list
    
    def move_to_pix(self, component_name, pix_x:int, pix_y:int): 
        """
        - Desc -
        component_name 의 이름을 갖는 Component 를 pix_x, pix_y 위치로 이동
        """
        to_x = pix_x * self.__resolution
        to_y = pix_y * self.__resolution
        self.components_dict[component_name].move_to(Point(to_x, to_y), inplace=True)
    
    def rotation(self, component_name, angle):
        """
        - Desc -
        component_name 의 이름을 갖는 Component 를 angle 만큼 회전
        angle은 90 도 단위로 입력
        
        """
        self.components_dict[component_name].rotation(angle, inplace=True)
    
    def get_component_img(self, component_name:str, img_size:tuple, fill=True):
        """
        - Desc -
        component_name 의 이름을 갖는 Component 의 CV 이미지를 반환
        """
        comp = self.components_dict[component_name]
        return comp.get_cv_img_center(size = img_size, fill = fill)
    
    def switch_component_layer(self, component_name:str):
        """
        - Desc -
        component_name 의 이름을 갖는 Component 의 layer 를 변경
        """
        
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
        min_x, max_x, min_y, max_y = self.get_size()
        ax.set_xlim([min_x, max_x])
        ax.set_ylim([min_y, max_y])
        ax.set_aspect('equal') #, 'box')
        
        if save:
            plt.savefig(dpi=dpi, fname=image_name)
        return fig, ax
        
    def get_size(self):
        """
        전체 PCB 사이즈를 반환 
        """
        return self.board.bounding_box
    
    def get_component(self, comp_name:str) -> Component:
        """
        - Desc -
        부품의 이름을 입력으로 받아서 component dict에서 해당 부품을 반환하는 method.
        
        - Input -
        name(str): 부품의 이름
        """
        return self.components_dict[comp_name]
    
    def merge_polygon(self, base_img:np.array, background:Polygon, foreground:Polygon, inplace = False) -> tuple[np.array, bool]:
        collision = False
        
        # foreground의 Polygon이 존재하지 않을 경우 예외처리 
        if len(foreground) == 0:
            return base_img, collision
        
        if inplace == False:
            base_img = copy.deepcopy(base_img)
        
        back_pix_h = int(round(background.h / self.__resolution, 0)) + 1
        back_pix_w = int(round(background.w / self.__resolution, 0)) + 1
        
        ## Component의 원점 매핑 시 BBox 계산. 
        moved_min_x = foreground.min_x - background.min_x
        moved_max_x = foreground.max_x - background.min_x
        moved_min_y = foreground.min_y - background.min_y 
        moved_max_y = foreground.max_y - background.min_y 

        ## Pixel 영역에서의 BBox 영역 매핑 
        min_pix_h = back_pix_h - 1 - int(round((moved_max_y / self.__resolution), 0))
        max_pix_h = back_pix_h - 1 - int(round((moved_min_y / self.__resolution), 0))
        min_pix_w = int(round((moved_min_x / self.__resolution), 0))
        max_pix_w = int(round((moved_max_x / self.__resolution), 0))

        ## 이미지 범위 검사 
        if (min_pix_h < 0) or (min_pix_w < 0) or (max_pix_h > back_pix_h) or (max_pix_w > back_pix_w):
            return base_img, True

        ## 이미지 삽입
        partial_base_img = base_img[min_pix_h:min_pix_h+foreground.get_cv_img().shape[0], min_pix_w:min_pix_w+foreground.get_cv_img().shape[1]]
        
        ## 이미지 삽입 시, 이미지 크기가 다를 경우 예외처리
        if partial_base_img.shape != foreground.get_cv_img().shape :
            raise Exception(f'이미지의 사이즈는 ', partial_base_img.shape, ', 부품의 사이즈는 ', foreground.get_cv_img().shape, \
                f'놓고자하는 부품의 Pixel 영역에서의 BBox 영역은 ', min_pix_h, max_pix_h, min_pix_w, max_pix_w, ' 이고, 이미지의 Pixel 영역에서의 최대 사이즈는 ', back_pix_h, back_pix_w)
        
        if ((partial_base_img == 0) & (foreground.get_cv_img() == 0)).sum() > 0: 
            collision = True
        else: 
            base_img[min_pix_h:min_pix_h+foreground.get_cv_img().shape[0], min_pix_w:min_pix_w+foreground.get_cv_img().shape[1]] = foreground.get_cv_img() 
        return base_img, collision
    
    # def merge_component(self, component_name:str, inplace=True) -> list[bool]:
    #     '''
    #     - Desc -
        
    #     '''
    #     collision = [False, False]
    #     comp = self.get_component(component_name)
    #     polyg = [comp.top_area, comp.bottom_area]
        
    #     for i in range(2):
    #         self.state[i], collision[i] = self.merge_polygon(self.state[i], self.board, polyg[i], inplace=inplace)
    #     return collision
    
    def put_component(self, component_name:str, pix_x:int, pix_y:int, inplace=True) -> bool:
        """
        - Desc -
        부품을 특정 위치에 놓는 Method. 
        부품의 좌측상단 픽셀위치를 기준으로 놓음.
        부품이 기존 이미지와 충돌할 경우, 충돌 여부를 반환함.
        충돌 발생 시, self.state 를 업데이트 하지 않음.  
        
        - Input -
        component_name(str): 
        pix_x(int): 부품의 좌측 상단 픽셀의 x 좌표 
        pix_y(int): 부품의 좌측 상단 픽셀의 y 좌표 
        inplace(bool):
        
        - Output -
        collision(bool): 충돌 여부. True 면 충돌, False 면 정상. 
        """
        
        # pix_x, pix_y type check
        assert isinstance(pix_x, int), 'pix_x must be integer type' 
        assert isinstance(pix_y, int), 'pix_y must be integer type' 
        
        if pix_x < 0 or pix_y < 0:
            return False
            # raise Exception('Pixel 좌표는 양수여야 함')
        
        comp = self.get_component(component_name)
        
        ## 이미지 범위 검사 
        max_pos_x = pix_x + comp.cv_top_img.shape[1]
        max_pos_y = pix_y + comp.cv_top_img.shape[0]
        
        if (max_pos_y > self.state[0].shape[0]) or (max_pos_x > self.state[0].shape[1]):
            return True # 이미지가 범위를 벗어나는 경우 충돌
        
        top_partial = self.state[0][pix_y:max_pos_y, pix_x:max_pos_x]
        bottom_partial = self.state[1][pix_y:max_pos_y, pix_x:max_pos_x]
        
        if (((top_partial == 0) & (comp.cv_top_img == 0)).sum() > 0) or (((bottom_partial == 0) & (comp.cv_bottom_img == 0)).sum() > 0): 
            return True # 충돌
        else: 
            # 해당 Position 에 부품 삽입
            self.state[0][pix_y:max_pos_y, pix_x:max_pos_x] = (~((self.state[0][pix_y:max_pos_y, pix_x:max_pos_x] == 0) | (comp.cv_top_img == 0))).astype('int') * 255
            self.state[1][pix_y:max_pos_y, pix_x:max_pos_x] = (~((self.state[1][pix_y:max_pos_y, pix_x:max_pos_x] == 0) | (comp.cv_bottom_img == 0))).astype('int') * 255
        
            # 삽입된 부품의 위치정보 수정 
            ## pixel을 float 영역으로 수정 
            min_x = pix_x * self.__resolution
            max_y = (self.state[0].shape[1] - pix_y - 1) * self.__resolution
            center_x = (comp.max_x - comp.min_x) / 2 + min_x
            center_y = max_y - (comp.max_y - comp.min_y) / 2

            # float 영역에서의 component 이동 
            comp.move_to(Point(center_x, center_y), inplace=True)
            
        comp.placed = True
        return False

    
    
    

