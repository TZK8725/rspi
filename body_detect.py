import cv2
import numpy as np
import time

body_image = cv2.imread("/home/pi/Desktop/image/body-image/body_test.png")
w, h, c = body_image.shape
image = cv2.resize(body_image, (int(h/3), int(w/3)))

detect_image = image
# detect_image = body_image
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
start = time.time()
locations, weights = hog.detectMultiScale(detect_image, scale=1.07, winStride=(8, 8))
end = time.time()

print(locations, weights)
for body, w in zip(locations, weights):
    if w >0.9:
        color = (111, 222, 33)
    else:
        color = (255, 255, 255)
    x, y, w, h = body
    cv2.rectangle(detect_image, (x, y), (x+w, y+h), color, 2)
print(end-start)
# cv2.imshow("image", body_image)
cv2.imshow("image2", image)
cv2.waitKey()
