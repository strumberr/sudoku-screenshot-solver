#author - strumber
#github - https://github.com/strumberr

#This model does not recognize most fonts, font training pytesseract, will be necessary if it should be expanded.
#It is not accurate around 10-20% due to the font and color changes between different sudokus. Finer tuning would be necessary if expanded.

import cv2
import numpy as np
import os
from pytesseract import image_to_string
from PIL import Image
from random import randint
import time
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re

img_path = "Screenshot 2023-01-23 021855.png"
img = cv2.imread(img_path, cv2.COLOR_BGR2GRAY)
(thresh, blackAndWhiteImage) = cv2.threshold(img, 170, 255, cv2.THRESH_BINARY)
cv2.imwrite("sudoku_ex_bw.png", blackAndWhiteImage)
img = cv2.imread("sudoku_ex_bw.png", cv2.COLOR_BGR2GRAY)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(gray,50,255,0)
contours,hierarchy = cv2.findContours(thresh, 1, 2)

print("Number of contours detected:", len(contours))

n_of_squares = 0
list_xywh = []
for cnt in contours:
    x1,y1 = cnt[0][0]
    approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
    if len(approx) == 4:
        x, y, w, h = cv2.boundingRect(cnt)
        dict = {
            "w":
            {"x": x, 
            "y": y, 
            "w": w, 
            "h": h}}
        list_xywh.append(dict)
        ratio = float(w)/h
        if ratio >= 0.9 and ratio <= 1.1:
            r = randint(0, 255)
            g = randint(0, 255)
            b = randint(0, 255)
            rand_color = (r, g, b)
            #print(rand_color)
            if w > 100 and h > 100:
                img = cv2.drawContours(img, [cnt], -1, (255, 255, 255), 1)
                print(f"w = {w}, h = {h}")
                n_of_squares += 1
                one_third_y = y + (h/3)
                one_third_x = x + (w/3)
                two_third_y = y + (h/3)*2
                two_third_x = x + (w/3)*2
                three_third_y = y + (h/3)*3
                three_third_x = x + (w/3)*3
                
                if w > 400 and h > 400:
                    pass
                else:
                    cv2.line(img, (x, int(one_third_y)), (x+w, int(one_third_y)), (255, 255, 255), 2)
                    cv2.line(img, (int(one_third_x), y), (int(one_third_x), y+h), (255, 255, 255), 2)

                    cv2.line(img, (x, int(two_third_y)), (x+w, int(two_third_y)), (255, 255, 255), 2)
                    cv2.line(img, (int(two_third_x), y), (int(two_third_x), y+h), (255, 255, 255), 2)

                    cv2.line(img, (x, int(three_third_y)), (x+w, int(three_third_y)), (255, 255, 255), 2)
                    cv2.line(img, (int(three_third_x), y), (int(three_third_x), y+h), (255, 255, 255), 2)
        else:
            r = randint(0, 255)
            g = randint(0, 255)
            b = randint(0, 255)

#sort the list by width of the square (w)
list_xywh.sort(key=lambda x: x['w']['w'], reverse=True)
print(list_xywh[0]['w'])
cv2.rectangle(img, (list_xywh[0]['w']['x'], list_xywh[0]['w']['y']), (list_xywh[0]['w']['x']+list_xywh[0]['w']['w'], list_xywh[0]['w']['y']+list_xywh[0]['w']['h']), (255, 255, 255), 2)
low = np.array([0, 0, 0])
up = np.array([255, 255, 255])
mask = cv2.inRange(img, low, up)
#remove mask from image using coordinates above
img = img[list_xywh[0]['w']['y']:list_xywh[0]['w']['y']+list_xywh[0]['w']['h'], list_xywh[0]['w']['x']:list_xywh[0]['w']['x']+list_xywh[0]['w']['w']]
cv2.imwrite("output.jpg", img)
#get image resolution
height, width, channels = img.shape
square_y = height/9
square_x = width/9
#coordinates of top left corner of each square
list_of_squares = []

for i in range(9):
    for j in range(9):
        dict = {
            "x": square_x*j,
            "y": square_y*i,
            "w": square_x,
            "h": square_y
        }
        list_of_squares.append(dict)
print(list_of_squares)

all_numbers = []
#crop each square by masking it out, then move on to the next square and repeat and run OCR on each square
for i in range(81):
    #crop each square
    img = cv2.imread("output.jpg")
    img = img[int(list_of_squares[i]['y']):int(list_of_squares[i]['y']+list_of_squares[i]['h'] + 5), int(list_of_squares[i]['x'] + 5):int(list_of_squares[i]['x']+list_of_squares[i]['w'])]
    scale_percent = 65 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    window_name = "Sudoku"
    cv2.imshow(window_name, img)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    cv2.waitKey(1)
    
    pytesseract.pytesseract.tesseract_cmd = r'D:\tesseract\tesseract.exe'
    def getText():
        HSV_img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(HSV_img)
        thresh = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        txt = image_to_string(thresh, config="--psm 6 digits whitelist=123456789")
        if txt == '':
            txt = "0"
        txt_replace = txt.replace("\n", "")
        return txt_replace
     
    text = getText()
    all_numbers.append(text)

joined = ''.join(all_numbers)

joined_list = re.findall('.........',joined)

new_list = []
for el in joined_list:
    list_thing = []
    for el in el:
        list_thing.append(int(el))

    new_list.append(list_thing)

print(new_list)
        
list_solved = []

M = 9
def puzzle(a):
    for i in range(M):
        for j in range(M):
            print(a[i][j],end = " ")
            list_solved.append(a[i][j])
        print()
def solve(grid, row, col, num):
    for x in range(9):
        if grid[row][x] == num:
          
            return False
             
    for x in range(9):
        if grid[x][col] == num:
          
            return False
 
 
    startRow = row - row % 3
    startCol = col - col % 3
    for i in range(3):
        for j in range(3):
            if grid[i + startRow][j + startCol] == num:
                return False
    return True
 
def Suduko(grid, row, col):
 
    if (row == M - 1 and col == M):
        return True
    if col == M:
      
        row += 1
        col = 0
        
    if grid[row][col] > 0:
        return Suduko(grid, row, col + 1)
      
    for num in range(1, M + 1, 1): 
     
        if solve(grid, row, col, num):
         
            grid[row][col] = num
            
            if Suduko(grid, row, col + 1):
                return True
        grid[row][col] = 0
        
    return False

grid = new_list
 
if (Suduko(grid, 0, 0)):
    puzzle(grid)
else:
    print("No solution")

#print(text)

list_list = []

for el in list_solved:
    list_list.append(str(el))

new_numberinos = ''.join(list_list)

list_solved_new = re.findall('.........',new_numberinos)
print(f"list - {list_solved_new}")

#coordinates of top left corner of each square
list_of_squares = []

for i in range(9):
    for j in range(9):
        dict = {
            "x": square_x*j+20,
            "y": square_y*i+30,
            "w": square_x,
            "h": square_y
        }
        list_of_squares.append(dict)
print(list_of_squares)

new_img = cv2.imread("output.jpg")
height, width, channels = new_img.shape
print(f"height - {height}, width - {width}, channels - {channels}")
img = np.ones((height, width, 3), dtype = np.uint8)
img = 255* img

for el, text in zip(list_of_squares, new_numberinos):
    cv2.putText(img, str(text), (int(el['x']), int(el['y'])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    print(f"el - {el['x']}, {el['y']} - text - {text}")
cv2.imwrite("output2.jpg", img)


#window_name = "Sudoku"

#cv2.imshow(window_name, img)
#cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
#cv2.waitKey(0)
