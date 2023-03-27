import cv2

ori_img = cv2.imread('./tests/test_floodfill.png')
ori_img = cv2.cvtColor(ori_img, cv2.COLOR_BGR2GRAY)
ret, img = cv2.threshold(ori_img, 127, 255, cv2.THRESH_BINARY)


fill_val = 100 

height = img.shape[0]
width = img.shape[1]

# 상, 하 라인 
for col in range(img.shape[1]):
    if img[0, col] == 255:
        print(0, col, img[0, col])
        cv2.floodFill(img, mask=None, seedPoint=(col, 0), newVal=fill_val)
        
    if img[height-1, col] == 255:
        print(height-1, col, img[height-1, col])
        cv2.floodFill(img, mask=None, seedPoint=(col, height-1), newVal=fill_val)

# 좌, 우 라인 
for row in range(img.shape[0]):
    if img[row, 0] == 255:
        print(row, 0, img[row, 0])
        cv2.floodFill(img, mask=None, seedPoint=(0, row), newVal=fill_val)
        
    if img[row, width-1] == 255:
        print(row, width-1, img[row, width-1])
        cv2.floodFill(img, mask=None, seedPoint=(width-1, row), newVal=fill_val)

inner_index = img != fill_val
img[inner_index] = 0
img[~inner_index] = 255

# 결과 이미지 출력
cv2.imshow("Result1", img)
cv2.imshow("Result2", ori_img)
cv2.waitKey(0)
cv2.destroyAllWindows()