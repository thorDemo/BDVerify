import paramiko
import platform
import os
from paramiko.ssh_exception import SSHException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class EVInit:

    def __init__(self):
        self.local = os.path.normcase(os.path.abspath('.'))  # 项目相对路径
        self.host = "23.110.211.170"  # 服务器host
        self.root = "root"  # 账号
        self.password = "Gchao@888"  # 密码
        self.remote_path = '/www/wwwroot/xbw/'  # 远程提交路径
        self.local_path = self.local + '/down/'  # 本地上传路径

    def judge_environmental(self):
        """
        判断控制器路径 和cookie路径
        :return:
        """
        sys_str = platform.system()
        if sys_str == "Windows":
            chrome_path = self.local + "/driver/chromedriver.exe"  # 谷歌控制器路径
            chrome_profile = 'C:/Users/username/AppData/Local/Google/Chrome/User Data/test_profile'

        else:
            chrome_path = self.local + "/driver/chromedriver"  # 谷歌控制器路径
            chrome_profile = '/Users/hexiaotian/Library/Application Support/Google/Chrome/Default'

        return chrome_path, chrome_profile

    def ssh_login(self):
        print('正在连接SSH服务器')
        while True:
            transport = paramiko.Transport((self.host, 223))
            try:
                transport.connect(username=self.root, password=self.password)
                sftp = paramiko.SFTPClient.from_transport(transport)
                print('服务器连接成功')
                break
            except SSHException as e:
                print('服务器连接失败 尝试连接服务器...')

        return sftp

    def chrome_login(self):
        options = webdriver.ChromeOptions()
        chrome_path, chrome_profile = self.judge_environmental()
        #  'profile.managed_default_content_settings.images': 1
        #  'profile.default_content_settings.popups': 0,
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': self.local_path,
            'profile.managed_default_content_settings.images': 1,
        }
        options.add_argument("--user-data-dir=" + chrome_profile)
        options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(chrome_path, chrome_options=options)  # 打开 Chrome 浏览器
        driver.implicitly_wait(2)  # seconds
        # driver.get("https://ziyuan.baidu.com/login/index?u=/site/index")
        print('登陆成功')
        driver.get("https://ziyuan.baidu.com/site/index")
        cookie = driver.get_cookies()
        print(cookie)

        return driver

