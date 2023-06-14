#%%
from abc import *
import numpy as np
import heapq
import itertools
import math
from itertools import combinations
import os
import json
import sys
#%%
from abc import *
from pcb_parser.geometry import Point
from pcb_parser.parser import PCB
from typing import Union
#%%

class Router:
    def __init__(self, PCB, resolution = 0.005):
        self.__resolution = resolution
        self.pcb = PCB
        self.pcb.update_resolution(resolution)
        self.put_components()
        
        wire_name_list = list(self.pcb.net_list.keys())
        self.net = {wire_name:(tuple(zip(self.pcb.net_list[wire_name].name, self.pcb.net_list[wire_name].pin_no))) for wire_name in wire_name_list}

    @property
    def resulotion(self):
        return self.__resolution

    @resulotion.setter
    def resulotion(self, resolution:float):
        return Router(self.PCB, resolution=resolution)
        
    def get_redraw_map(self, resolution:float):
        """
        - Desc -
        새로운 Resolution 에 맞춰서 새로운 객체를 추출  
        
        - Input -
        resolution(float):
        
        """
        return Router(self.PCB, resolution=resolution)
     

    def put_components(self):
        for comp_name in self.pcb.components_dict.keys():
            comp = self.pcb.get_component(comp_name)

            # comp 좌표 -> Integer
            pix_x = self.float2pix(comp.min_x)
            pix_y = self.float2pix(comp.min_y)
            
            self.pcb.put_component(comp_name, pix_x, pix_y, inplace=True)

    def float2pix(self, x:float) -> int:
        '''
        float 영역의 값을 pixel 값으로 변경 
        '''
        return int(round(x / self.__resolution, 0))

    def pix2float(self, pix_x:int) -> float:
        '''
        pixel 영역의 값을 float 값으로 변경 
        '''
        return pix_x * self.__resolution

    def get_pin_position(self, comp_name:str, pin_num:Union[str, int]) -> Point:
        """
        - Desciption -
        특정 component의 Pin 번호 입력 시, 해당 핀의 위치를 반환해주는 메소드. 

        - Input -
        comp_name(str): Component 이름  
        pin_num(int): Component의 Pin 번호 
        
        - Output -
        Point(Point): 해당 핀의 Point 객체 
        
        """
        comp = self.pcb.get_component(comp_name)
        comp_center = comp.center
        pin_position = comp_center + comp.pin_dict[str(pin_num)].position
        return pin_position

    def astar(self, start_node:tuple[int], goal_node:tuple[int], state:np.array, wire_num:int):
        """
        state : rl 학습시 들어가게되는 state 정보
        start_node : 시작 node 
        goal_node : 도착 node, 핀의 위치
        """
        
        assert state.shape[0]==2, "state shape must be 2 channel"
        
        # 그래프의 가로, 세로 길이
        channel, height, width = state.shape
        
        start_x, start_y, start_z = start_node[1], start_node[2], start_node[0]
        goal_x, goal_y, goal_z = goal_node[1], goal_node[2], goal_node[0] 
        
        # 각 노드의 이전 노드를 기록하는 딕셔너리
        parent_nodes = {}
        
        # g: Start Node 에서 해당 노드까지의 실제 소요 경비값
        # 시작 노드로의 거리는 0, 그 외는 무한대로 초기화
        g_score = {node: float('inf') for node in np.ndindex(state.shape)}
        size  = sys.getsizeof(g_score)
        print(f"메모리 크기: {size} 바이트")
        
        g_score[start_node] = 0
        
        # 시작 노드로의 예상 거리값 계산
        f_score = {node: abs(goal_node - node[0]) + abs(goal_node - node[1]) + abs(goal_node - node[2]) for node in np.ndindex(state.shape)}
        f_score[start_node] = abs(goal_x - start_x) + abs(goal_y - start_y) + abs(goal_z - start_z)
    
        # 방문한 노드를 기록하는 set
        visited_nodes = set()
        
        # 우선순위 큐 생성 (f_score를 기준으로 작은 값이 우선순위가 높게 설정)
        priority_queue = []
        heapq.heappush(priority_queue, (f_score[start_node], start_node))
        
        while priority_queue:
            # 우선순위 큐에서 가장 우선순위가 높은 노드 선택
            current_node = heapq.heappop(priority_queue)[1]
            
            # 도착점에 도달한 경우
            if current_node == goal_node:
                path = [current_node] # 도착 지점의 Node 
                while current_node in parent_nodes:
                    current_node = parent_nodes[current_node]
                    path.append(current_node)
                path.reverse()
                return path
            
            # 현재 노드를 방문 처리
            visited_nodes.add(current_node)
            
            # 이웃 노드들 순회
            # z 축 추가 하기
            for neighbor_node in [(current_node[0], current_node[1] - 1, current_node[2]),
                                (current_node[0], current_node[1] + 1, current_node[2]),
                                (current_node[0], current_node[1], current_node[2] - 1),
                                (current_node[0], current_node[1], current_node[2] + 1),
                                (current_node[0] - 1, current_node[1], current_node[2]),
                                (current_node[0] + 1, current_node[1], current_node[2])]:
                # 이웃 노드가 그래프 내에 있고, 벽이 아니며, 이미 방문하지 않은 노드인 경우
                if ((0 <= neighbor_node[0] < channel) and (0 <= neighbor_node[1] < width) and (0 <= neighbor_node[2] < height) and (neighbor_node not in visited_nodes)):

                    # 이웃 노드가 벽이거나 다른 노드의 시작 및 끝 지점이 아닐 경우 
                    if (state[neighbor_node] == 0) or (state[neighbor_node] == wire_num) :
                        
                        # 현재 노드를 거쳐서 이웃 노드에 도달할 때의 예상 거리값 계산
                        tentative_g_score = g_score[current_node] + 1
                        
                        if tentative_g_score < g_score[neighbor_node]:
                            # 이웃 노드까지의 거리가 더 짧은 경우
                            parent_nodes[neighbor_node] = current_node
                            g_score[neighbor_node] = tentative_g_score
                            f_score[neighbor_node] = tentative_g_score + abs(goal_x - neighbor_node[1]) + abs(goal_y - neighbor_node[2]) +abs(goal_z - neighbor_node[0])
                            
                            # 우선순위 큐에 추가
                            heapq.heappush(priority_queue, (f_score[neighbor_node], neighbor_node))
        
        # 도착점에 도달할 수 없는 경우
        return None
    
    def draw_wires(self):
        to_pred_wire_nums = [wire.wire_num for wire in self.wires]
        hist_list = []
        c_list = []
        print("wire 예측넘버:", to_pred_wire_nums)
        while to_pred_wire_nums:

            wire_num = to_pred_wire_nums.pop(0)
            path = self.find_path(self.find_wire(wire_num), self.draw_map)
                 
            if path is None:
                path = self.find_path(self.find_wire(wire_num), self.default_map)

                if path is None:#두번 다 None이면 path 값을 False
                    return False
                else:
                    c_list = self.get_collision_path(path,wire_num)
                    self.draw_wire(wire_num, path)
                    [self.convert_to_zero(self.find_wire(c)) for c in c_list]
                     
            else:
                self.draw_wire(wire_num, path)
                

        return True 
            
    
    def routing(self,wire_name:str,wire_num:int):
        #wire_num 1000 부터
        """
        특정 wire_name에 대한 라우팅 알고리즘
        default_map : 기본 맵
        draw_map : 라우팅을 진행할 맵
        """
        default_map = np.stack(self.pcb.state)
        draw_map = np.stack(self.pcb.state.copy())
        
        wire_list = self.net[wire_name]
        pair_comp = list(combinations(wire_list, 2))
        
        # wire_number 는 연결되어있는 와이어 개수로
        
        for i, p in enumerate(pair_comp):
            #print(p)
            start_point = self.get_pin_position(p[0][0], p[0][1])
            goal_point = self.get_pin_position(p[1][0], p[1][1])
           
            #
            start_layer = 0 if self.pcb.get_component(p[0][0]).placed_layer=='TOP' else 1 
            goal_layer = 0 if self.pcb.get_component(p[1][0]).placed_layer=='TOP' else 1 
            
            start_node = (start_layer, *(start_point.get_pix(self.__resolution)))
            goal_node = (goal_layer,*(goal_point.get_pix(self.__resolution)))
            
            path = self.astar(start_node,goal_node,draw_map,wire_num)
            if path is None:
                path = self.astar(start_node, goal_node, default_map, wire_num)
                if path is None:
                    return False
                else:
                    
                    return False          
        return 

#%%
if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    with open("/VOLUME/PNR/data/sample_data.json", 'r') as f:
        data = json.load(f)

    pcb = PCB(data)
    router = Router(pcb,resolution=0.01)
    wire_name = 'SIGN1118' 
    router.routing(wire_name,1000)
    
# %%
