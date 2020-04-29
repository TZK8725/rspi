import random
import os
import cv2
import numpy as np
from skimage.feature import hog
from sklearn.svm import SVC
import joblib
from sklearn.model_selection import train_test_split


def warpAffine(img):

    M = np.float32([[1, 0, random.randint(-5, 5)],[0, 1, random.randint(-5, 5)]])
    img_ = cv2.warpAffine(img, M, dsize=(64, 64) )
    return img_

def rotat(img):

    M = cv2.getRotationMatrix2D((32, 32), random.randint(-15, 15), 1)
    img_ = cv2.warpAffine(img, M, dsize=(64, 64) )
    return img_

def random_img(img):

    choice = random.choice([1, 2])
    if choice == 1:
        img_ = warpAffine(img)
    else:
        img_ = rotat(img)

    return img_

def get_img(dir_path, i):

    img_list = os.listdir(dir_path)
    img_path = os.path.join(dir_path, random.choice(img_list)) 
    img_list.append(str(i)+".jpg")
    return img_path

def save_img(dir_path, img, i):

    cv2.imwrite(dir_path+"\\{}.jpg".format(i), img)

def get_none_img(img_path, save_path):

    i = 401   
    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    while True:
        save_path_ = save_path + "%d.jpg"%i
        x = random.randint(0, w-64)
        y = random.randint(0, h-64)
        new_img = img[y:y+64, x:x+64]
        cv2.imwrite(save_path_, new_img)
        i+=1
        if i > 2000:
            break
    # cv2.imshow("new", new_img)
    # cv2.waitKey()


def get_hog_feature(all_img_list):

    hog_feature_list = list()
    labels_list = list()
    for img_path in all_img_list:
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        features = hog(gray)
        hog_feature_list.append(features)
        label = get_labels(img_path)
        labels_list.append(label)
    return hog_feature_list, labels_list

def get_labels(img_path:str):

    path_list = img_path.split("/")
    label = path_list[-2]   
    return label

def get_img_list(path_list):

    all_img_list = list()
    for path in path_list:
        img_list = os.listdir(path)
        img_path_list = [os.path.join(path, i) for i in img_list]
        all_img_list.extend(img_path_list)
    return all_img_list


def svm_train(features, labels, save_path="./model.pkl"):

    feature_train, feature_test, label_train, label_test = train_test_split(features, labels, test_size=0.25)
    clf = SVC(C=10, probability=True, kernel='rbf')
    clf.fit(feature_train, label_train)
    clf = joblib.load(save_path)
    score = clf.score(feature_test, label_test)
    print(score)
    if os.path.isfile(save_path):
        os.remove(save_path)
    
    joblib.dump(clf, save_path)

def recognition(img):

    img = cv2.resize(img, (64, 64))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    feature = hog(gray)
    features = [feature]
    clf = joblib.load("./model.pkl")
    result = clf.predict(features)
    return result


if __name__ == "__main__":

    img_path_list = ["/home/pi/Desktop/image/TSD/no_park/", "/home/pi/Desktop/image/TSD/20t/", "/home/pi/Desktop/image/TSD/60/", "/home/pi/Desktop/image/TSD/none/", "/home/pi/Desktop/image/TSD/40/"]
    all_img_list = get_img_list(img_path_list)
    hog_feature_list, labels_list = get_hog_feature(all_img_list)
    # print(labels_list)
    svm_train(hog_feature_list, labels_list)

    # dir_path = "G:/image-dataset/TSD/20t"
    # i = 0
    # while True:
    #     img_path = get_img(dir_path, i)
    #     img = cv2.imread(img_path)
    #     img = cv2.resize(img, (64, 64))
    #     img_ = random_img(img)
    #     save_img(dir_path, img_, i)
    #     i+=1
    #     if i > 499:
    #         break

    # none_dir_path = "C:/Users/TZK/Desktop/test_image/test13.png"
    # save_path = "G:/image-dataset/TSD/none/"
    # get_none_img(none_dir_path, save_path)

