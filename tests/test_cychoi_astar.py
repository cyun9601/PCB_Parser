import heapq
import numpy as np
from datetime import datetime

def check_collision(point, paths):
    for path in paths:
        if point in path:
            return True
    return False

def calculate_paths(nmap, pairs):
    paths = []
    for pair in pairs:
        path = astar(nmap, pair[0], pair[1])
        if path == False:
            return False
        paths.append(path)
        for point in path:
            if check_collision(point, paths):
                # If there is a collision, set the cell in the map to 1 (a wall) to force a recalculation
                nmap[point[0]][point[1]][point[2]] = 1
                # Then, recalculate the path
                new_path = astar(nmap, pair[0], pair[1])
                if new_path == False:
                    return False
                # Replace the old path with the new one
                paths[-1] = new_path
    return paths

def heuristic(a, b):
    return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2 + (b[2] - a[2]) ** 2)

def astar(array, start, goal):
    neighbors = [
        (0, 1, 0),
        (0, -1, 0),
        (1, 0, 0),
        (-1, 0, 0),
        (0, 0, 1),
        (0, 0, -1)
    ]

    close_set = set()
    came_from = {}
    gscore = {start:0}
    fscore = {start:heuristic(start, goal)}
    oheap = []

    heapq.heappush(oheap, (fscore[start], start))
    
    while oheap:
        current = heapq.heappop(oheap)[1]

        # print(len(came_from))

        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data

        close_set.add(current)
        for i, j, k in neighbors:
            neighbor = current[0] + i, current[1] + j, current[2] + k
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:
                    if 0 <= neighbor[2] < array.shape[2]:                
                        if array[neighbor[0]][neighbor[1]][neighbor[2]] == 1:
                            continue
                    else:
                        # array bound z walls
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue
                
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue
                
            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                # print("current : ", current)
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))
                
    return False

# Define the 3D grid (it could be your map)

nmap = np.zeros(shape = (2, 1000, 10000))

# np.array([
#     [[0, 0, 0],
#     [0, 0, 0],
#     [0, 0, 0]],
    
#     [[0, 0, 0],
#     [0, 0, 0],
#     [0, 0, 0]],

#     [[0, 0, 0],
#      [0, 0, 0],
#      [0, 0, 0]]
# ])
 
st_time = datetime.now()
astar(nmap, (0, 0, 0), (0, 100, 100))
consume_time = datetime.now() - st_time
print(consume_time)

st_time = datetime.now()
astar(nmap, (0, 0, 0), (0, 5000, 5000))
consume_time = datetime.now() - st_time
print(consume_time)

st_time = datetime.now()
astar(nmap, (0, 0, 0), (0, 9999, 9999))
consume_time = datetime.now() - st_time
print(consume_time)

