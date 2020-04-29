import os
import time
import cv2
from no_key import NoKey, Display


def face_detect(disp=None):
    
    cap = cv2.VideoCapture(0)
    classifier = cv2.CascadeClassifier("/home/pi/Desktop/haar/haarcascade_frontalface_alt.xml")
    ret, i = 1, 0
    start_time = time.time()
    
    while ret:

        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if disp is not None:
            disp.display_image(gray)
        faceRects = classifier.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=4, minSize=(60, 60))

        if len(faceRects) > 0:
            i += 1 
            if i > 2:
                if len(faceRects) == 1:
                    x, y, w, h = faceRects[0]
                    image = gray[x:y, x+w:y+h]
                else :
                    image = None
                cv2.imwrite("/home/pi/face-rec/detect_image.jpg", frame)
                statu = True
                break 
        # cv2.imshow("tzk", gray)
        key = cv2.waitKey(20)
        if key & 0xFF == ord("q"):
            statu = False
            image = None
            break
        end_time = time.time()
        if (end_time-start_time) > 10:
            statu = False
            image = None
            break
    cap.release()
    cv2.destroyAllWindows()
    disp.clear() 
    return statu, image

if __name__ == "__main__":

    nokey = NoKey()
    disp = Display()
    detect_image = "/home/pi/face-rec/detect_image.jpg"

    while True:
        print(nokey.check_body())
        if nokey.check_body() == 1:
            if nokey.check_light():
                nokey.led_open()
 
            det, image = face_detect(disp=disp)
            if det :
                disp.display_image(image)
                verify_score, face_token, access_token = nokey.face_verify(detect_image)

                if verify_score > 0.3:
                    compare_score  = nokey.face_compare(face_token, access_token)
                    if compare_score > 90:
                        disp.display_text("解锁成功 \nヾ(≧▽≦*)o")                      
                        nokey.unlock()
                        nokey.send_info("解锁成功", "注意安全")
                        content, data = nokey.get_content(detect_image, True)
                        nokey.send_more_info("成功", content)
                        nokey.post_data(data)
                        break
                    else:
                        disp.display_text("解锁失败\n请重试 :(")
                        nokey.send_info("解锁失败", "认证得分：%d"%compare_score)
                        content, data = nokey.get_content(detect_image, False)
                        nokey.send_more_info("认证失败", content)
                        nokey.post_data(data)
                else:
                    nokey.send_info("活体认证失败", "得分：%d"%verify_score)
                    content, data = nokey.get_content(detect_image, False)
                    nokey.send_more_info("活体认证失败", content)
                    nokey.post_data(data)
                os.remove(detect_image)
            nokey.led_close()
    nokey.clean_gpio()
    disp.clear()