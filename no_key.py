'''
一些对GPIO的组件
'''

import datetime
import RPi.GPIO as GPIO
import base64
from time import sleep
import requests
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import cv2
import leancloud


class NoKey(object):

    def __init__(self):

        self.ak = '6EdKHXpGto1Ger4agphehXjg'
        self.sk = 'g99OC68xKlaFYgOgCXFd9t13pjAmE737'
        self.access_path = "/home/pi/face-rec/access.txt"
        self.source_img = "/home/pi/Desktop/image/face-image/证件照.jpg"
        self.upload_url = "https://doc.sm.ms/upload"
        self.source = "s-40960cea-419e-4670-bc2f-c48829a5"
        self.receiver = "g-20671ffc-7c02-4e74-bd13-1060cc3f"

        # 对GPIO接口初始化
        self.light = 18 #12
        self.body = 17 #11
        self.s_led = 27 #13
        self.s_lock = 22 #15
        self.sound =  23 #16

        out_list = [self.s_led, self.s_lock, self.sound]
        in_list = [self.light, self.body]
        
        GPIO.setmode(GPIO.BCM)        
        GPIO.setup(out_list, GPIO.OUT, initial=1)
        GPIO.setup(in_list, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def check_light(self):

        # 环境光线检测模块
        result = GPIO.input(self.light)
        return result

    def check_body(self):

        # 人体检测模块
        sleep(0.5)
        result = GPIO.input(self.body)
        return result
        # return 1

    def led_open(self):

        # 控制LED模块
        GPIO.output(self.s_led, 0)
    def led_close(self):
        
        GPIO.output(self.s_led, 1)

    def unlock(self):

        # 解锁模块
        GPIO.output(self.s_lock, 0)
        sleep(10)
        GPIO.output(self.s_lock, 1)

    def sound(self):

        # 声音提醒模块
        for i in range(3):
            GPIO.output(self.sound, 0)
            sleep(0.5)
            GPIO.output(self.sound, 1)
            sleep(0.3)

    @staticmethod
    def send_info(title, info):

        # 发送信息模块
        url= "https://api.day.app/YCghPEfvUpW9RV3xudNzyG/%s/%s"%(title, info)
        response = requests.get(url)

    def send_more_info(self, title: str, content: str):

        data = {
            "source": self.source,
            "receiver": self.receiver,
            "content": content,
            "title": title
        }
        requests.post("https://api.alertover.com/v1/alert", data=data)

    @staticmethod
    def post_data(data:dict):

        leancloud.init("tLdWjcuTkiqUOSN33wknu4Xw-gzGzoHsz", "Jkj5V5zCR7MeV3tWMq8JUJse")
        DataBase = leancloud.Object.extend("Unlock")
        db = DataBase()
        for key in data:
            db.set(key, data[key])
        db.save()

    @staticmethod
    def get_content(image_path, ret:bool):
        
        with open (image_path, "rb") as f:
            image = f.read()
        header = {
            "Content-Type": "multipart/form-data",
            "Authorization": "WL2weyAtF3X7jNipIeZMMOqwuY0nKIHh"
            }
        param = {"smfile": image}

        response = requests.post("https://sm.ms/api/v2/upload", files=param, data=header)
        # print(response.json())
        if response.json()["success"]:
            image_url = response.json()["data"]["url"]
        content = "时间：{} \n图片：{}".format(datetime.datetime.now(), image_url)
        data = {
            "time": datetime.datetime.now(),
            "success": ret,
            "image": image_url
        }

        return content, data

    def _get_token(self):

        url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s'%(self.ak, self.sk)      
        response = requests.get(url)
        if response.status_code == 200:
            access_token = response.json()["access_token"]
            with open(self.access_path, "w") as f:
                f.write(access_token)
            return access_token
    
    def face_verify(self, unknown_image):
        
        #活体检测模块
        with open(unknown_image, "rb") as f:
            uk_img = base64.b64encode(f.read()).decode()

        params = "[{\"image\": \"%s\", \"image_type\": \"BASE64\", \"option\": \"COMMON\" }]"%(uk_img)
        headers = {'content-type': 'application/json'}
        api = "https://aip.baidubce.com/rest/2.0/face/v3/faceverify?access_token="

        with open(self.access_path, "r") as f:
            access_token = f.read()
        response = requests.post(api+access_token, data=params, headers=headers)
        if response.json()["error_code"] == 110 or 111:
            access_token = self._get_token()
            response = requests.post(api+access_token, data=params, headers=headers)
        if response.json()["error_msg"] == "SUCCESS":
            score = response.json()["result"]["face_liveness"]
            face_token = response.json()["result"]["face_list"][0]["face_token"]
            return score, face_token, access_token
        else:
            self.send_info("异常", response.json())
            return 0

    def face_compare(self, face_token, access_token):

        # 人脸验证模块
        with open (self.source_img, "rb") as f:
            src_img = base64.b64encode(f.read()).decode()
        api = "https://aip.baidubce.com/rest/2.0/face/v3/match?access_token="+access_token
        params = "[{\"image\": \"%s\", \"image_type\": \"BASE64\", \"face_type\": \"CERT\"}, {\"image\": \"%s\", \"image_type\": \"FACE_TOKEN\"}]"%(src_img, face_token)
        headers = {'content-type': 'application/json'}
        response = requests.post(api, data=params, headers=headers)
        
        if response.json()["error_msg"] == "SUCCESS":
            score = response.json()["result"]["score"]
            return score
        else:
            print(response.json()) 
            return 0

    @staticmethod
    def clean_gpio(self):
        GPIO.cleanup()


class Display(object):

    def __init__(self):

        # pioled 模块初始化
        self.font_size = 18
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)

        self.height = self.disp.height
        self.width = self.disp.width
        self.disp.begin()
        self.disp.clear()
        self.font = ImageFont.truetype("/home/pi/fonts/simhei.ttf", size=self.font_size)

    def display_image(self, image_array):

        # 显示图像模块
        image = Image.fromarray(image_array)
        image = image.resize((self.width, self.height))
        image = image.convert("1")
        self.disp.image(image)
        self.disp.display()
    
    def display_text(self, text):
        
        # 显示文字模块
        font = self.font
        image = Image.new("1", size = (self.width, self.height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.width, self.height), fill=0, outline=0)
        draw.text((5, (self.height-self.font_size*2)/2), text=text, fill=255, font=font)

        self.disp.image(image)
        self.disp.display()

    def display_image_text(self, img, text):

        font = self.font
        image = Image.new("1", size = (self.width, self.height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.width, self.height), fill=0, outline=0)
        image_array = Image.fromarray(img)
        draw.bitmap((0, 0), image_array, 1)
        draw.text((64, (self.height-self.font_size*2)/2), text=text, fill=255, font=font)

        self.disp.image(image)
        self.disp.display()

    def clear(self):
        self.disp.clear()
        self.disp.display() 


if __name__ == "__main__":

    nokey = NoKey()
    # try:
    #     while True:
    #         print(nokey.check_light())
    #         if nokey.check_light() == 1:
    #             nokey.led_open()
    #         else:
    #             nokey.led_close()
    # except KeyboardInterrupt():
    #     nokey.clean_gpio()
    # nokey.unlock()
    # sleep(3)
    # GPIO.cleanup()   
    # with open("/home/pi/Desktop/image/test4.jpg", "rb") as f:
    #     img = f.read()
    # score, face_token, access_token = nokey.face_verify(img)
    # # print(score, face_token)
    # if score > 0.98:
    #     compare_score  = nokey.face_compare(face_token, access_token)
    #     if compare_score > 90:
    #         nokey.send_info("解锁成功", "注意安全")
    #     else:
    #         nokey.send_info("解锁失败", "认证得分：%d"%compare_score)
    # else:
    #     nokey.send_info("error", "活体认证失败"
    # try:
    #     while True:
    #         sleep(0.5)
    #         print(nokey.check_body())
    # except KeyboardInterrupt:
    #     pass
    # GPIO.cleanup()
    # disp = Display()
    # cap = cv2.VideoCapture(0)
    # ret = True
    # try:
    #     while ret:

    #         ret, frame = cap.read()
    #         image_array = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #         disp.display_image(image_array)

    #         key = cv2.waitKey(20)
    #         if key & 0xFF == ord("q"):
    #             break
    # except KeyboardInterrupt:
    #     # disp.clear()
    #     disp.display_text("你好吗")
    #     sleep(0.5)
    #     disp.display_text("你好")
    #     sleep(0.5)
    #     disp.display_text("你")

