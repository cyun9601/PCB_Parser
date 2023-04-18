#%%
import heapq
from math import sqrt

import sys 
import os 
import json
import cv2 
import matplotlib.pyplot as plt  

#%%
class Node:
    def __init__(self, x, y, z, cost, heuristic, parent):
        self.x = x
        self.y = y
        self.z = z
        self.cost = cost
        self.heuristic = heuristic
        self.parent = parent

    def __lt__(self, other):
        return self.cost + self.heuristic < other.cost + other.heuristic

#유클리디안 거리 
def heuristic(a, b):
    return sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)

#
def astar(start, goal):
    open_set = []
    closed_set = set()
    heapq.heappush(open_set, start)

    while open_set:
        current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current.parent:
                path.append(current)
                current = current.parent
            path.append(current)
            return path[::-1]

        closed_set.add(current)
#(0, -1), (0, 1), (-1, 0), (1, 0)
        for x, y, z in [(0, -1, 1), (0, 1, 1), (-1, 0, 1), (1, 0, 1), (0, -1, 0), (0, 1, 0), (-1, 0, 0), (1, 0, 0)]:
            neighbor = Node(current.x + x, current.y + y, current.z + z, 0, 0, current)
            if neighbor in closed_set:
                continue
            neighbor.cost = current.cost + 1
            neighbor.heuristic = heuristic(neighbor, goal)
            if neighbor not in open_set:
                heapq.heappush(open_set, neighbor)
            else:
                for i, n in enumerate(open_set):
                    if n == neighbor and neighbor.cost < n.cost:
                        open_set[i] = neighbor
                        heapq.heapify(open_set)
                        break

    return None

start_node = Node(0, 0, 0, 0, 0, None)
goal_node = Node(4, 4, 0, 0, 0, None)

path = astar(start_node, goal_node)

if path is None:
    print("No path found")
else:
    for node in path:
        print(f"({node.x}, {node.y}, {node.z})")


#



# %%
