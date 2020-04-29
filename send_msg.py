import requests
import time
import subprocess

def test_net():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
        response = requests.get("https://www.baidu.com/", headers=headers)
        if response.status_code == 200:
            # print(response.status_code)
            return True
        else:
            time.sleep(2)
            test_net()
    except:
        time.sleep(3)
        test_net()
def get_ip():
    ifconfig = subprocess.getoutput("hostname -I")

    # title = "ip_address"
    # ip = re.findall("inet(.*?)netmask", ifconfig)
    ip = ifconfig.split(' ')
    msg = "inet4 = %s,\rinet6 = %s"%(ip[0], ip[1])
    return msg
def send_ip(msg):
    title = "ip_address"
    basic_url = "https://api.day.app/YCghPEfvUpW9RV3xudNzyG/%s/%s"%(title, msg)
    response = requests.get(basic_url)
    while True:
        if response.json()["code"] == 200:
            break
        else:
            time.sleep(2)

if __name__ == "__main__":
    # print("start")
    result = test_net()
    if result:
        msg = get_ip()
        send_ip(msg)
