import cv2
import numpy as np 

img = np.ones((1000, 1000, 3)) * 255

direction = 'CCW'
s_angle = 512.18140
e_angle = 387.8183218

if direction == 'CCW':
    s = 360 - e_angle
    e = 360 - s_angle

    if s > e : 
        e = e + 360

print(s, e)

# 원점 (50,300), 반지름50, 회전0, 0도부터 360도 그리기
cv2.ellipse(img, (150, 150), (13, 13), 0, 360 - 387.8183218, 360 - 512.18140 + 360, (0,0,255))

s_angle = 332.1814016
e_angle = 207.818321

if direction == 'CCW':
    s = 360 - e_angle
    e = 360 - s_angle

    if s > e : 
        e = e + 360

print(s, e)

# cv2.ellipse(img, (300, 150), (30, 30), 0, s, e, (0, 0, 255))
cv2.ellipse(img, (300, 150), (13, 13), 0, 152.18, 387.81, (0, 0, 255))



s_angle = 0
e_angle = 360

if direction == 'CCW':
    s = 360 - e_angle
    e = 360 - s_angle

    if s > e : 
        e = e + 360

print(s, e)

cv2.ellipse(img, (450, 150), (30, 30), 0, s, e, (0, 0, 255))


cv2.imshow('circle', img)
cv2.waitKey(0)
cv2.destroyAllWindows()