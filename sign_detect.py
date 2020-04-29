import time
import cv2
import numpy as np
from no_key import Display
import joblib
from skimage.feature import hog


def get_sign(img):

    # img = cv2.imread(image)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(img_hsv, np.array([0, 46, 46]), np.array([10,255,255]))
    mask2 = cv2.inRange(img_hsv, np.array([156, 50, 50]), np.array([180,255,255]))
    mask = mask1 + mask2
    mask_blur = cv2.medianBlur(mask, ksize=11)

    img_edge = cv2.Canny(mask_blur, 50, 150)
    sign = cv2.adaptiveThreshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 21, 4)
    hough = cv2.HoughCircles(img_edge, cv2.HOUGH_GRADIENT, minDist=40, dp=1, param2=40, minRadius=33, maxRadius=100)
    mask_circle = np.zeros(img.shape[:2], np.uint8)
    try:
        for i in hough[0] :
            cv2.circle(mask_circle, (i[0], i[1]), i[2], (255, 255, 255), -1)
            roi = cv2.bitwise_and(sign, mask_circle)
            sign = roi[int(i[1]-i[2]) : int(i[1]+i[2]), int(i[0]-i[2]) : int(i[0]+i[2])]
            detect_sign = img[int(i[1]-i[2]) : int(i[1]+i[2]), int(i[0]-i[2]) : int(i[0]+i[2])]
    except:
        sign = None
        detect_sign = None
    finally:
        return sign, detect_sign
# _, sign = cv2.threshold(cv2.cvtColor(sign, cv2.COLOR_BGR2GRAY), 80, 255, cv2.THRESH_BINARY)


if __name__ == "__main__":

    disp = Display()
    disp.clear()
    cap = cv2.VideoCapture(0)
    clf = joblib.load("model.pkl")
    ret = 1
    font = cv2.FONT_HERSHEY_COMPLEX
    while ret:
        
        ret, img = cap.read()
        # print(img.shape)
        resize = (int(img.shape[1]/2), int(img.shape[0]/2))
        img = cv2.resize(img, resize)
        # print(img.shape)
        start1 = time.time()
        sign, detect_sign = get_sign(img)
        print(time.time()-start1)
        if sign is not None and sign.shape[0] > 64 and sign.shape[1] >64:
            start2 = time.time()
            sign = cv2.resize(sign, (64, 64))
            detect_sign = cv2.resize(detect_sign, (64, 64))
            feature = hog(detect_sign)
            # print(feature)
            result = clf.predict([feature])
            print(result[0],"\n检测时长：{}".format(time.time()-start2))
            # disp.display_image(sign)
            # disp.display_text(result[0])
            disp.display_image_text(sign, result[0])    
            # time.sleep(3)
            # disp.clear()
            
            cv2.putText(img, result[0], color=(120, 220, 100), org=(30, 30), fontFace=font, thickness=1, fontScale=1)
            cv2.imshow("sign", detect_sign)
            
        cv2.imshow("img", img)
        cv2.waitKey(25)
    
    