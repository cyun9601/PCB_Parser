import numpy as np
import heapq
import math 

class Point:
    def __init__(self, x, y) -> None:
        self.x = x 
        self.y = y

class Wire: 
    def __init__(self) -> None:
        pass

def get_collision_wire(array:np.array, path:list[tuple], wire_num:int):
    v_list = []
    for p in path: 
        v_list.append(array[p[0], p[1]])
    return list(set(v_list) - {wire_num})

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


if __name__=='__main__':
    
    '''
    --------------------------
    | S1 | E2 | X1 |    |    |
    -------------------------- 
    |    |    |    |    |    |
    -------------------------- 
    |    | S3 |    | E3 |    |
    --------------------------
    |    |    |    |    |    |
    -------------------------- 
    | E1 | S2 |    | X2 |    |
    -------------------------- 
    '''
   
    S1 = Point(0, 0)
    S2 = Point(4, 1)
    S3 = Point(2, 1)
    
    E1 = Point(4, 0)
    E2 = Point(0, 1)
    E3 = Point(2, 3)
    
    X1 = Point(0, 2)
    X2 = Point(4, 3)
    
    start_points = [S1, S2, S3]
    end_points = [E1, E2, E3]
    occlusion_points = [X1, X2]
    
    array = np.zeros((5, 5)).astype(int)
    
    for i, start_point in enumerate(start_points, 1):
        if array[start_point.x, start_point.y] == 0:
            array[start_point.x, start_point.y] = i
        else: 
            raise ('다른 포인트와 충돌')
    for i, end_point in enumerate(end_points, 1):
        if array[end_point.x, end_point.y] == 0:
            array[end_point.x, end_point.y] = i
        else:
            raise ('다른 포인트와 충돌')
    for i, occlusion_point in enumerate(occlusion_points, 1):
        if array[occlusion_point.x, occlusion_point.y] == 0:
            array[occlusion_point.x, occlusion_point.y] = -1
        else:
            raise ('다른 포인트와 충돌')
    
    print("array: \n", array)
    
    # draw가 반영되는 Array
    draw_array = array.copy()
    to_pred_wires = []
    complete_wires = []
    
    for i, (start_point, end_point) in enumerate(zip(start_points, end_points), 1):
        path = astar(start_point.x, start_point.y, end_point.x, end_point.y, draw_array, wire_num=i)
        print("첫 시도 시 Path: ", path)
        
        if path is None: 
            path = astar(start_point.x, start_point.y, end_point.x, end_point.y, array, wire_num=i)
            print("두번째 시도 시 Path: ", path)
            collision_wires = get_collision_wire(draw_array, path, i)
            for p in path: 
                draw_array[p[0], p[1]] = i
            
            for wire in collision_wires: 
                draw_array.where(wire) # <- 0
            
        if path is not None: 
            for p in path: 
                draw_array[p[0], p[1]] = i
        
        # print(path_collision(array, path))