from math import inf

def bellman_ford(graph, source):
    """
    위 코드에서 graph는 딕셔너리로 구현된 그래프를 나타내며, 각 노드를 키(key)로 갖고 해당 노드와 이어진 노드와 가중치를 값(value)으로 갖는 딕셔너리
    입니다. source는 최단 경로의 시작점이 될 노드입니다.

    dist는 노드들의 최단 거리를 나타내는 딕셔너리입니다. dist[node]는 시작점으로부터 노드 node까지의 최단 거리를 의미합니다.

    알고리즘은 먼저 모든 노드의 최단 거리를 무한대로 초기화합니다. 그리고 모든 간선을 반복하면서 최단 거리를 갱신합니다. 
    
    이 때 dist[u] + weight < dist[v]인 경우에만 최단 거리를 갱신합니다. 마지막으로 음수 사이클을 검사하고, 
    
    음수 사이클이 있다면 None과 함께 "Negative cycle detected" 메시지를 반환합니다.

    알고리즘의 시간 복잡도는 O(VE)입니다.
    """

    # 그래프에서 노드들의 수를 구합니다.
    nodes = list(graph.keys())
    num_nodes = len(nodes)
    
    # 모든 노드의 최단 거리를 무한대로 초기화합니다.
    dist = {node: inf for node in nodes}
    dist[source] = 0
    
    # 모든 간선을 반복하면서 최단 거리를 갱신합니다.
    for i in range(num_nodes - 1):
        for u in nodes:
            for v, weight in graph[u].items():
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
    
    # 음수 사이클을 검사합니다.
    for u in nodes:
        for v, weight in graph[u].items():
            if dist[u] + weight < dist[v]:
                return None, "Negative cycle detected"
    
    return dist, None


import heapq
import math

def heuristic(a, b):
    # 휴리스틱 함수: 두 노드 사이의 유클리드 거리 계산
    return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

def astar(array, start, goal):
    # 시작 노드와 목표 노드의 좌표
    start = tuple(start)
    goal = tuple(goal)
    
    # 이웃 노드를 찾기 위한 방향 벡터
    neighbors = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
    
    # 노드의 우선순위를 결정하기 위한 우선순위 큐
    heap = []
    # 시작 노드의 우선순위를 0으로 설정하고 큐에 추가
    heapq.heappush(heap, (0, start))
    
    # 노드에서 시작점까지의 최단 경로 저장
    came_from = {}
    # 노드에서 시작점까지의 실제 거리 저장
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while heap:
        # 우선순위가 가장 높은 노드 선택
        current = heapq.heappop(heap)[1]
        
        if current == goal:
            # 목표 노드에 도착했으면 최단 경로 반환
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path, cost_so_far[goal]
        
        # 이웃 노드 탐색
        for i, j in neighbors:
            next_node = current[0] + i, current[1] + j
            # 배열 범위를 벗어나면 무시
            if next_node[0] < 0 or next_node[0] >= len(array) or next_node[1] < 0 or next_node[1] >= len(array[0]):
                continue
            # 벽이면 무시
            if array[next_node[0]][next_node[1]] == 1:
                continue
            # 다음 노드까지의 비용 계산
            new_cost = cost_so_far[current] + 1
            # 다음 노드까지의 예상 비용 계산
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + heuristic(goal, next_node)
                heapq.heappush(heap, (priority, next_node))
                came_from[next_node] = current

        r




import heapq

def dijkstra(graph, start, end):
    # 시작 노드에서 각 노드까지의 거리를 저장할 딕셔너리
    distances = {vertex: float('inf') for vertex in graph}
    distances[start] = 0
    
    # 우선순위 큐
    pq = [(0, start)]
    
    # 최단 경로 저장할 딕셔너리
    previous_vertices = {vertex: None for vertex in graph}
    
    while len(pq) > 0:
        # 우선순위가 가장 높은 노드 선택
        current_distance, current_vertex = heapq.heappop(pq)
        
        # 이미 방문한 노드인 경우 건너뜀
        if current_distance > distances[current_vertex]:
            continue
        
        # 인접한 노드 탐색
        for neighbor, weight in graph[current_vertex].items():
            # 현재 노드에서 인접한 노드까지의 비용
            distance = current_distance + weight
            
            # 현재 노드를 거쳐서 인접한 노드까지 가는 것이 더 빠른 경우
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_vertices[neighbor] = current_vertex
                heapq.heappush(pq, (distance, neighbor))
        
        # 목표 노드에 도착하면 경로 반환
        if current_vertex == end:
            path = []
            while previous_vertices[current_vertex] is not None:
                path.append(current_vertex)
                current_vertex = previous_vertices[current_vertex]
            path.append(start)
            path.reverse()
            return path, distances[end]
    
    # 목표 노드에 도달할 수 없으면 None 반환
    return None, None


#%%
import sys 
sys.path.append('/VOLUME/PNR/hjwon/PCB_Parser/src/')
import pcb_parser
from pcb_parser import PCB
import os 
import json
import cv2 
import matplotlib.pyplot as plt  

os.chdir(os.path.abspath(os.path.dirname(__file__)))

with open("/VOLUME/PNR/data/sample_data.json", 'r') as f:
    data = json.load(f)

## PCB 객체 생성     
pcb = PCB(data)
pcb.pcb_info


group = []
for component_name, v in pcb.components_dict.items():
    #print(component_name, len(v.top_area), len(v.bottom_area))

    #fig = plt.figure(figsize=figsize, dpi=dpi)
    #ax = fig.add_subplot(111)
    # ax.xaxis.set_visible(False)
    # ax.yaxis.set_visible(False)

    comp = pcb.components_dict[component_name]
    
    group.append(comp.group)
# %%

print(set(group))
# %%
import heapq

def shortest_path(graph, start, end):
    """
    Dijkstra 알고리즘을 사용하여 최단 경로를 찾는 함수
    """
    queue = [(0, start, [])]
    visited = set()
    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node not in visited:
            visited.add(node)
            path = path + [node]
            if node == end:
                return (cost, path)
            for neighbor, c in graph[node].items():
                if neighbor not in visited:
                    heapq.heappush(queue, (cost + c, neighbor, path))
    return float('inf')

def add_obstacle(graph, obstacle, neighbors):
    """
    물체의 위치를 노드로 추가하고 간선을 연결하는 함수
    """
    for node, dist in neighbors.items():
        if node in graph:
            graph[node][obstacle] = dist
            graph[obstacle][node] = dist
        else:
            graph[node] = {obstacle: dist}
            graph[obstacle] = {node: dist}

# 예제 그래프
graph = {
    'A': {'B': 5, 'C': 1},
    'B': {'A': 5, 'C': 2, 'D': 1},
    'C': {'A': 1, 'B': 2, 'D': 4},
    'D': {'B': 1, 'C': 4, 'E': 1},
    'E': {'D': 1, 'F': 2},
    'F': {'E': 2}
}

# 물체 추가 - 충돌 방지
add_obstacle(graph, 'C1', {'C': 1})
add_obstacle(graph, 'D1', {'D': 1})

# 최단 경로 찾기
print(shortest_path(graph, 'A', 'F'))

# %%
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc as mpl_Arc
# 원점 (50,300), 반지름50, 회전0, 0도부터 360도 그리기
fig = plt.figure(figsize=(10, 10), dpi=300)
ax = fig.add_subplot(111)
# 1
ax.add_patch(mpl_Arc((4, 0), width = 0.75*2, height = 0.75*2, angle=0, theta1=0, theta2=360))
# 2
ax.add_patch(mpl_Arc((2, 0), width = 0.75*2, height = 0.75*2, angle=0, theta1=0, theta2=360))
# 3
ax.add_patch(mpl_Arc((0, 0), width = 0.75*2, height = 0.75*2, angle=0, theta1=0, theta2=360, color='r'))
# 4
ax.add_patch(mpl_Arc((-2, 0), width = 0.75*2, height = 0.75*2, angle=0, theta1=0, theta2=360, color='r'))
# 5
ax.add_patch(mpl_Arc((-4, 0), width = 0.75*2, height = 0.75*2, angle=0, theta1=0, theta2=360, color='r'))
# 6
#ax.add_patch(mpl_Arc((0, -1.5), width = 0.05*2, height = 0.05*2, angle=0, theta1=207.8185, theta2=332.1843, color='r'))
# 7
#ax.add_patch(mpl_Arc((-2, 0), width = 0.75*2, height = 0.75*2, angle=0, theta1=512.18140, theta2=387.8183218, color='r'))
#ax.add_patch(mpl_Arc((-2, 0), width = 0.75*2, height = 0.75*2, angle=0, theta1=512.18140, theta2=387.8183218, color='r'))
#ax.add_patch(mpl_Arc((-2, 0), width = 0.75*2, height = 0.75*2, angle=0, theta1=512.18140, theta2=387.8183218, color='r'))
ax.set_aspect('equal') #, 'box')
plt.xlim([-10, 10])
plt.ylim([-10, 10])
plt.show()
# plt.savefig(dpi=dpi, fname=f'./comp/{comp.part_name}_BOTTOM.png')
# %%
