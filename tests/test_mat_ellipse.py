import matplotlib.pyplot as plt 
import numpy as np 
from matplotlib.patches import Arc as mpl_Arc

img = np.ones((1000, 1000, 3)) * 255

# 원점 (50,300), 반지름50, 회전0, 0도부터 360도 그리기
fig = plt.figure(figsize=(10, 10), dpi=300)

ax = fig.add_subplot(111)
# ax.xaxis.set_visible(False)
# ax.yaxis.set_visible(False)
ax.add_patch(mpl_Arc(center = (4, 2.0465), width = 0.75*2, height = 0.75*2, angle=0, theta1=332.18, theta2=207.81))
ax.set_aspect('equal') #, 'box')
plt.show()
# plt.savefig(dpi=dpi, fname=f'./comp/{comp.part_name}_BOTTOM.png')