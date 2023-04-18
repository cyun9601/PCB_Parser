#%%
import numpy as np
import heapq
import math 
from typing import Union 

class Point:
    def __init__(self, x, y) -> None:
        self.x = x 
        self.y = y

    def __repr__(self) -> str:
       
        return f'{self.x},{self.y}'
        
class Wire:
     
    def __init__(self,start:Point,end:Point,wire_num) -> None:
        self.start = start
        self.end = end
        self.wire_num = wire_num
        self.path = [start,end]

        
    def initialize(self) -> None:
        self.path = [self.start, self.end]
        self.connected = False

    def __repr__(self) -> str:
        return f'{self.start}, {self.end}'

class History: 
    def __init__(self, wire_num, c_list, to_pred_wire_nums) -> None:
        self.wire_num = wire_num
        self.c_list = c_list
        self.to_pred_wire_nums = to_pred_wire_nums
    
    def __eq__(self, other: object) -> bool:
        if (self.wire_num == other.wire_num) & (self.c_list == other.c_list) & (self.to_pred_wire_nums == other.to_pred_wire_nums):
            return True
        else:
            return False

class Router:
    def __init__(self, map:np.array, wires:list[Wire]):
        self.default_map = map # start , end , collision point 반영된 array #초기값
        self.draw_map = map.copy() #그려지는 캔버스 map
        self.wires = wires
        
    def get_size(self):
        """
        grid의 사이즈 반환
        """
        return self.default_map.shape

    def find_path(self,wire,array) -> Union[list, None] :    
        path = astar(wire.start.x,wire.start.y,wire.end.x,wire.end.y, array, wire_num=wire.wire_num)
        
        return path     
    
    def get_collision_path(self,path,wire_num) -> list[int]:
        """
        충돌된 와이어의 번호를 반환        
        """
        v_list = []
        for p in path: 
            v_list.append(self.draw_map[p[0], p[1]])    
        
        return list(set(v_list) - {wire_num} -{0})
        
    # 다른 wire path 끼리의 충돌을 검사하는 함수
    def is_conflict(self, array, path) -> bool:
        """
        detect conflict between wires
        """
        v_list = []
        for p in path: 
            v_list.append(array[p[0], p[1]])
        
        if set(v_list) & {wire.wire_num}:
            return False
        else:
            return True
    
    def convert_to_zero(self, wire):
        """
        충돌된 wire의 번호를 배열에서 0으로 바꿔서 return
        wire: 충돌된 wire
        wire.initialize() : 충돌된 wire의 path를 초기화
        """  
        self.draw_map[np.where(self.draw_map == wire.wire_num)] = 0
        wire.initialize()
        self.draw_map[wire.start.x, wire.start.y] = wire.wire_num
        self.draw_map[wire.end.x, wire.end.y] = wire.wire_num
        
        #print(self.draw_map)

    def find_wire(self,wire_num):
        """
        wire_num에 해당하는 wire를 반환
        """
        for wire in self.wires:
            if wire.wire_num == wire_num:
                return wire
    
    def draw_wire(self,wire_num,path):
        """
        wire를 그리는 함수
        path: Wire의 path
        array: 그려지는 배열 ex. self.draw_map: 계속 바뀌는 배열, self.default_map: 초기값
    
        """
        if path is None:
            raise "path is None"
        else:
            wire = self.find_wire(wire_num)
            wire.path = path
            wire.connected = True
            for p in path:
                self.draw_map[p[0], p[1]] = wire.wire_num
            
                            
    def draw_wires(self):
        
        to_pred_wire_nums = [wire.wire_num for wire in self.wires]
        print("wire 예측넘버:", to_pred_wire_nums)
        while to_pred_wire_nums:
            wire_num = to_pred_wire_nums.pop(0)
            path = self.find_path(self.find_wire(wire_num), self.draw_map)
            #print("첫번째 경로 그리기:",path)
            if path is None:
                path = self.find_path(self.find_wire(wire_num), self.default_map)
                
                #print("충돌 후 경로:",path)
                #print(self.default_map)
                if path is None:
                    return False
                else:
                    #print("충돌 후 그림 그리기")
                    c_list = self.get_collision_path(path,wire_num)
                    self.draw_wire(wire_num, path)
                    #print("충돌된 경로구하기:", path,to_pred_wire_num)
                    #print(self.draw_map)
                    #print("충돌된 wire:",c_list)
                    [self.convert_to_zero(self.find_wire(c)) for c in c_list]
                    to_pred_wire_nums.extend(c_list)
                    # self.draw_collision_wires(c_list)
            else:
                self.draw_wire(wire_num, path)
        


        return True 
            

def heuristic(s:Point, e:Point):
    # 휴리스틱 함수: 두 노드 사이의 유클리드 거리 계산
    return abs(s[0] - e[0]) + abs(s[1] - e[1])


def astar(start_x:int, start_y:int, goal_x:int, goal_y:int, graph:np.array, wire_num:int):
    # 그래프의 가로, 세로 길이
    height, width = graph.shape
    
    # 시작점, 도착점 노드 생성
    start_node = (start_x, start_y)
    goal_node = (goal_x, goal_y)
    
    # 각 노드의 이전 노드를 기록하는 딕셔너리
    parent_nodes = {}
    
    # g: Start Node 에서 해당 노드까지의 실제 소요 경비값. 
    # 시작 노드로의 거리는 0, 그 외는 무한대로 초기화
    g_score = {node: float('inf') for node in np.ndindex(graph.shape)}
    g_score[start_node] = 0
    
    # 시작 노드로의 예상 거리값 계산
    f_score = {node: abs(goal_x - node[0]) + abs(goal_y - node[1]) for node in np.ndindex(graph.shape)}
    f_score[start_node] = abs(goal_x - start_x) + abs(goal_y - start_y)
    
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
        for neighbor_node in [(current_node[0] - 1, current_node[1]),
                            (current_node[0] + 1, current_node[1]),
                            (current_node[0], current_node[1] - 1),
                            (current_node[0], current_node[1] + 1)]:
            # 이웃 노드가 그래프 내에 있고, 벽이 아니며, 이미 방문하지 않은 노드인 경우
            if ((0 <= neighbor_node[0] < width) and (0 <= neighbor_node[1] < height) and (neighbor_node not in visited_nodes)):

                # 이웃 노드가 벽이거나 다른 노드의 시작 및 끝 지점이 아닐 경우 
                if (graph[neighbor_node] == 0) or (graph[neighbor_node] == wire_num) :
                    
                    # 현재 노드를 거쳐서 이웃 노드에 도달할 때의 예상 거리값 계산
                    tentative_g_score = g_score[current_node] + 1
                    
                    if tentative_g_score < g_score[neighbor_node]:
                        # 이웃 노드까지의 거리가 더 짧은 경우
                        parent_nodes[neighbor_node] = current_node
                        g_score[neighbor_node] = tentative_g_score
                        f_score[neighbor_node] = tentative_g_score + abs(goal_x - neighbor_node[0]) + abs(goal_y - neighbor_node[1])
                        
                        # 우선순위 큐에 추가
                        heapq.heappush(priority_queue, (f_score[neighbor_node], neighbor_node))
    
    # 도착점에 도달할 수 없는 경우
    return None


#%%
if __name__=='__main__':
    
    '''
    test case 추가
    -------------------------------
    |    |    | S3 | S4 |    |    |
    ------------------------------- 
    |    |    |    |    |    |    |
    ------------------------------- 
    | S1 |    |    |    |    | E1 | 
    -------------------------------
    | S2 |    |    |    |    | E2 |
    ------------------------------- 
    |    |    |    |    |    |    |
    -------------------------------
    |    |    | E3 | E4 |    |    |
    ------------------------------- 
    '''
    W1 = Wire(Point(2, 0),Point(2, 5),1)
    W2 = Wire(Point(3, 0),Point(3, 5),2)
    W3 = Wire(Point(0, 2),Point(5, 2),3)
    W4 = Wire(Point(0, 3),Point(5, 3),4)
   
 
    #좌측 상단
    X1 = Point(0, 0)
    X2 = Point(0, 4)
    X3 = Point(4, 0)
    X4 = Point(4, 4)
    


    #%%
    occlusion_points = [X1, X2, X3, X4]
    wires = [W1, W2, W3, W4]
    
    array = np.zeros((6, 6)).astype(int)
    
    
    for i, wire in enumerate(wires):
        if array[wire.start.x, wire.start.y] == 0:
            array[wire.start.x, wire.start.y] = wire.wire_num
        else: 
            raise ('다른 포인트와 충돌')    
        
        if array[wire.end.x, wire.end.y] == 0:
            array[wire.end.x, wire.end.y] = wire.wire_num
        else: 
            raise ('다른 포인트와 충돌')    
        
    for i, occlusion_point in enumerate(occlusion_points, 1):
        if array[occlusion_point.x, occlusion_point.y] == 0:
            #4 방향으로 4각형
            array[occlusion_point.x, occlusion_point.y] = -1
            array[occlusion_point.x+1, occlusion_point.y] = -1
            array[occlusion_point.x+1, occlusion_point.y+1] = -1
            array[occlusion_point.x, occlusion_point.y+1] = -1
        else:
            raise ('다른 포인트와 충돌')
    
    print("array: \n", array)
    
    router = Router(array, wires)
    #print(router.wires)#wire에 대한 list
    router.draw_wires()
    #print(router.draw_map)
