#힙 
#%%
import heapq
import numpy as np
import math

def heuristic(a, b):
    # 맨해튼 거리 계산
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

start = (6,0)
goal = (3,5)

neighbors = [(0,1),(0,-1),(1,0),(-1,0)]
close_set = set()
came_from = {}
gscore = {start:0}
fscore = {start:heuristic(start, goal)}
oheap = []

# %%
fscore
# %%
heapq.heappush(oheap, (fscore[start], start))
# %%
fscore[start]
# %%
(fscore[start], start)
# %%
oheap
# %%
heapq.heappop(oheap)[1]
# %%
fscore
# %%
neighbor = (6,1)
gscore.get(neighbor, 0)


# %%
heapq.heappush(oheap, (8, (6,1)))
# %%
oheap
# %%
oheap =[]
heapq.heappush(oheap, (fscore[start], start))
# %%
