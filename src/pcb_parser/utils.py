import cv2
import numpy as np 
import copy 
import os 

img_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comp_img')


def img_rot_90(img, k):
    return np.rot90(img, k=k)

def floodfill(img:np.array, fill_area = 'in', fill_val = 100):
    ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    
    height, width = img.shape
            
    # 상, 하 라인 
    for col in range(width):
        if img[0, col] == 255:
            cv2.floodFill(img, mask=None, seedPoint=(col, 0), newVal=fill_val)
            
        if img[height-1, col] == 255:
            cv2.floodFill(img, mask=None, seedPoint=(col, height-1), newVal=fill_val)

    # 좌, 우 라인 
    for row in range(height):
        if img[row, 0] == 255:
            cv2.floodFill(img, mask=None, seedPoint=(0, row), newVal=fill_val)
            
        if img[row, width-1] == 255:
            cv2.floodFill(img, mask=None, seedPoint=(width-1, row), newVal=fill_val)

    inner_index = img != fill_val
    if fill_area == 'in': 
        img[inner_index] = 0
        img[~inner_index] = 255
    elif fill_area == 'out':
        img[inner_index] = 255
        img[~inner_index] = 0
    return img