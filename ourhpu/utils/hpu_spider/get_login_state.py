import requests
import time
import re

from Crypto.Cipher import AES
from hashlib import sha1
from Crypto.Util.Padding import pad

import urllib.request
import urllib.parse
import base64
import json

# 获取加密的账号和密码
class Encrypted():
    def __init__(self, username, password, key_name, key_password):
        self.username = username
        self.password = password
        self.key_name = key_name
        self.key_password = key_password

    # 对username进行AES加密
    def encrypt(self, aes_str, key):
        """
        AES加密的几个参数：
        key: 密钥
        text: 加密内容
        model: 加密模式
        iv:偏移量
        """
        # 定义模式
        # 使用key,选择加密方式
        aes = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        pad_pkcs7 = pad(aes_str.encode('utf-8'), AES.block_size, style='pkcs7')  # 选择pkcs7补全
        encrypt_aes = aes.encrypt(pad_pkcs7)
        # 加密结果
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 解码
        encrypted_text_str = encrypted_text.replace("\n", "")
        # 此处我的输出结果老有换行符，所以用了临时方法将它剔除
        return encrypted_text_str

    def sha1_password(self):
        s1 = sha1()
        password = self.key_password + str(self.password)
        print(password)
        s1.update(password.encode("utf-8"))  # 转码（字节流）
        password2 = s1.hexdigest()
        return password2

    def run(self):
        username = self.encrypt(self.username, self.key_name)
        password = self.sha1_password()

        return username, password


class IdentifyPicture():
    def __init__(self):
        self.url = "https://ocrapi-advanced.taobao.com/ocrservice/advanced"
        AppCode = "9c8ef0d72c5040cdb00eab805c16166c"
        self.headers = {
            'Authorization': 'APPCODE ' + AppCode,
            'Content-Type': 'application/json; charset=UTF-8'
        }

    def get_code_num(self, picture_data):
        # 构造请求字典参数
        encodestr = str(base64.b64encode(picture_data), 'utf-8')

        picture_dict = {'img': encodestr}

        try:
            params = json.dumps(picture_dict).encode(encoding='UTF8')
            req = urllib.request.Request(self.url, params, self.headers)
            r = urllib.request.urlopen(req)
            html = r.read()
            r.close();
            return html.decode("utf8")
        except urllib.error.HTTPError as e:
            print(e.code)
            print(e.read().decode("utf8"))


class GetLoginMessage():
    def __init__(self, username, password):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
        }
        self.url = "http://218.196.248.100/eams/loginExt.action"
        self.base_url = "http://218.196.248.100/"
        self.username = username
        self.password = password

    def get_message(self):
        # 发起请求获取网页信息
        session = requests.session()
        req_str = session.get(self.url, headers=self.headers)
        # 获取key_username
        key_name = re.findall(r"encrypt\(username,'(.*?)'\)", req_str.text)[0]
        # 获取key_password
        key_password = re.findall(r"CryptoJS.SHA1\('(.*?)'", req_str.text)[0]

        username = self.username
        password = self.password

        # 对名字和密码进行加密
        login = Encrypted(username=username, password=password, key_name=key_name, key_password=key_password)
        username, password = login.run()
        # 获取验证码
        p = str(int(time.time()*1000))

        captcha_response = None
        while captcha_response is None:
            image = session.get(self.base_url + "eams/captcha/image.action?p="+p, headers=self.headers)
            # 获取验证码
            indetifypic = IdentifyPicture()
            html = indetifypic.get_code_num(image.content)

            captcha_json = json.loads(html)
            try:
                captcha_response = captcha_json["prism_wordsInfo"][-1]["word"]
            except Exception as e:
                pass

        # captcha_response = input("请输入验证码：")
        params1 = {
            "captcha_response": captcha_response
        }

        # 发起请求，设置验证码
        captcha_response_req = session.post("http://218.196.248.100/eams/loginExt!getCodeFlag.action", params=params1)
        flag = json.loads(captcha_response_req.text)["flag"]

        if flag:
            # 设置参数
            params2 = {
                "username": username,
                "password": password,
                "captcha_response": captcha_response,
                "session_locale": "zh_CN"
            }

            # 构造字典，发起请求
            session.post(self.url, headers=self.headers, params=params2)

            return session

        else:
            print("验证码不正确")

# if __name__ == '__main__':
#     get_message = GetLoginMessage("311722000118", "216514")
#     get_message.get_message()