from imutils.object_detection import non_max_suppression
import numpy as np
import argparse
import time
import cv2 as cv
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

def image2string(img, resize_num, b):
    # blur = cv.GaussianBlur(img,(5,5),0)
    # cv.addWeighted(blur,1.5,img,-0.5,0)
    # cv.imshow('temp', img)
    # cv.waitKey(0)
    im = Image.fromarray(cv.cvtColor(img, cv.COLOR_BGR2RGB))  
    # 影象放大
    im = im.resize((im.width * int(resize_num), im.height * int(resize_num)))
    # 影象二值化
    imgry = im.convert('L')
    # 對比度增強
    
    
    # imgry = imgry.filter(ImageFilter.SMOOTH)
    sharpness = ImageEnhance.Contrast(imgry)
    sharp_img = sharpness.enhance(b)
    
    sharp_img.show()

    content = pytesseract.image_to_string(sharp_img, lang = 'eng')
    if content != '':
        print('success!!')
    else:
        print('fail!!')
    return content
def determine_WH():

    

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type = str, help = "path to your input image")
ap.add_argument("-east", "--east", type = str, help = "path to input EAST text detector")
ap.add_argument("-c", "--min-confidence", type = float, default = 0.5, help = "minimum probability required to inspect a region")
ap.add_argument("-w", "--width", type = int, default = 320, help = "resized image width (should be multiple of 32)")
ap.add_argument("-e", "--height", type = int, default = 320, help = "resized image height (should be multiple of 32)")

args = vars(ap.parse_args())

image = cv.imread('test.png')
orig = image.copy()

(H, W) = image.shape[:2]

(newW, newH) = (1600, 1600)
rW = W / float(newW)
rH = H / float(newH)

image = cv.resize(image, (newW, newH))
(H, W) = image.shape[:2]

layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]

print("[INFO] loading EAST text detector...")

net = cv.dnn.readNet('frozen_east_text_detection.pb')
blob = cv.dnn.blobFromImage(image, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB = True, crop = False)
start = time.time()
net.setInput(blob)
(scores, geometry) = net.forward(layerNames)
end = time.time()

print("[INFO] text detection took {:.6f} seconds".format(end - start))

(numRows, numCols) = scores.shape[2:4]
rects = []
confidences = []

for y in range(0, numRows):
    scoresData = scores[0, 0, y]
    xData0 = geometry[0, 0, y]
    xData1 = geometry[0, 1, y]
    xData2 = geometry[0, 2, y]
    xData3 = geometry[0, 3, y]
    anglesData = geometry[0, 4, y]

    for x in range(0, numCols):
        if scoresData[x] < 0.3:
            continue
        
        (offsetX, offsetY) = (x * 4.0, y * 4.0)

        angle = anglesData[x]
        cos = np.cos(angle)
        sin = np.sin(angle)

        h = xData0[x] + xData2[x]
        w = xData1[x] + xData3[x]

        endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
        endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
        startX = int(endX - w)
        startY = int(endY - h)

        rects.append((startX, startY, endX, endY))
        confidences.append(scoresData[x])


boxes = non_max_suppression(np.array(rects), probs = confidences)

for (startX, startY, endX, endY) in boxes:
    # print(startX,startY,endX, endY)
    startX = max(int(startX * rW) - 5, 0)
    startY = max(int(startY * rH) - 5, 0)
    endX = min(int(endX * rW) + 5, orig.shape[1])
    endY = min(int(endY * rH) + 5, orig.shape[0])
    # print(startX,startY,endX, endY)
    # print(max(startX - 10, 0), min(endX + 10, image.shape[0] - 1), max(startY - 10, 0), min(endY + 10, image.shape[1] - 1))
    cv.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
    print(image2string(orig[startY : endY, startX : endX], 1, 4.0))
cv.imshow("Text Detection", orig)
cv.waitKey(0)


