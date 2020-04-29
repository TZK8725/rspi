import cv2
import joblib
frome no_key import NoKey, Display


class KunDetect(object):

    def __init__(self):

        self.face_classifier = cv2.CascadeClassifier("/home/pi/Desktop/haar/haarcascade_frontalface_alt.xml")
        self.sign_classifier = joblib.load("./model.pkl")
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    @staticmethod
    def videoRead(detect = None):
        cap = cv2.VideoCapture(0)
        ret = 1
        while True:
            ret, frame = cap.read()
            if detect is not None:
                detect(frame)
            cv2.waitKey(10)

    def faceDetect(self, frame):
        pass

    def bodyDetect(self, frame):
        pass

    def signDetect(self, frame):
        pass