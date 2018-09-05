# -*- coding=utf-8 -*-
import json, time, requests


class YDMHttp:

    def __init__(self):
        self.apiurl = 'http://api.yundama.com/api.php'
        self.username = 'ThorDemo'
        self.password = 'Ptyw1q2w3e$R'
        self.appid = str(1)
        self.appkey = '22cc5376925e9387a23cf797cb9ba745'

    def request(self, fields, files=[]):
        response = self.post_url(self.apiurl, fields, files)
        response = json.loads(response)
        return response
    
    def balance(self):
        data = {'method': 'balance', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response = self.request(data)
        if response:
            if response['ret'] and response['ret'] < 0:
                return response['ret']
            else:
                return response['balance']
        else:
            return -9001
    
    def login(self):
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response = self.request(data)
        if response:
            if response['ret'] and response['ret'] < 0:
                return response['ret']
            else:
                return response['uid']
        else:
            return -9001

    def upload(self, filename, codetype, timeout):
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
        file = {'file': filename}
        response = self.request(data, file)
        if response:
            if response['ret'] and response['ret'] < 0:
                return response['ret']
            else:
                return response['cid']
        else:
            return -9001

    def result(self, cid):
        data = {'method': 'result', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey, 'cid': str(cid)}
        response = self.request(data)
        return response and response['text'] or ''

    def decode(self, filename, codetype, timeout):
        cid = self.upload(filename, codetype, timeout)
        if cid > 0:
            for i in range(0, timeout):
                result = self.result(cid)
                if result != '':
                    return cid, result
                else:
                    time.sleep(1)
            return -3003, ''
        else:
            return cid, ''

    def report(self, cid):
        data = {'method': 'report', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey, 'cid': str(cid), 'flag': '0'}
        response = self.request(data)
        if response:
            return response['ret']
        else:
            return -9001

    def post_url(self, url, fields, files=[]):
        for key in files:
            files[key] = open(files[key], 'rb');
        res = requests.post(url, files=files, data=fields)
        return res.text

######################################################################


# # 用户名
# username = 'ThorDemo'
# # 密码
# password = 'Ptyw1q2w3e$R'
# appid = 1
# appkey = '22cc5376925e9387a23cf797cb9ba745'
# filename = 'gen.jpg'
# codetype = 2004
# timeout = 60
#
# # 初始化
# yundama = YDMHttp()
# # 登陆云打码
# uid = yundama.login()
# print('uid: %s' % uid)
#
# # 查询余额
# balance = yundama.balance()
# print('balance: %s' % balance)
#
# # 开始识别，图片路径，验证码类型ID，超时时间（秒），识别结果
# cid, result = yundama.decode(filename, codetype, timeout)
# print('cid: %s, result: %s' % (cid, result))

######################################################################
