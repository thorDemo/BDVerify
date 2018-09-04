from mylib.EVInit import EVInit
import time
import linecache
import os
from PIL import Image
from mylib.YDMHTTP import YDMHttp
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException


class BDVerify:

    def __init__(self):
        # 初始化
        self.en_init = EVInit()
        # 登录SFTP
        self.sftp = self.en_init.ssh_login()
        # 登录浏览器
        self.driver = self.en_init.chrome_login()
        # 初始化
        self.yundama = YDMHttp()
        # 登陆云打码
        self.uid = self.yundama.login()
        # 项目相对路径
        self.local = os.path.normcase(os.path.abspath('.'))
        # 本地上传路径
        self.upload_path = self.local + '/down/'
        # 远程上传路径
        self.remote_path = '/www/wwwroot/xbw/'
        print('uid: %s' % self.uid)

    def add_url(self, url):
        self.driver.get('https://ziyuan.baidu.com/site/siteadd')
        print('更改协议头')
        http = self.driver.find_element_by_xpath("//div[@id='protocolSelect']/input")
        self.driver.execute_script("arguments[0].value = 'http://'", http)
        print('添加url:' + url)
        send_url = self.driver.find_element_by_class_name('add-site-input')
        send_url.send_keys('www.' + url)
        self.driver.find_element_by_id('site-add').click()
        time.sleep(2)
        self.driver.find_element_by_id('captcha-img').click()
        while True:
            try:
                WebDriverWait(self.driver, 4).until(EC.visibility_of(self.driver.find_element_by_class_name('ml5')))
                code = self.get_code('add_url')
                input_code = self.driver.find_element_by_id('captcha')
                input_code.send_keys(code)
                self.driver.find_element_by_id('site-add').click()
                try:
                    time.sleep(1)
                    self.driver.find_element_by_id('check0')
                    return True
                except NoSuchElementException:
                    xpath = "/html/body/div[2]/div[3]/div[2]/div[4]/div[1]/span"
                    res = self.driver.find_element_by_xpath(xpath).text
                    if res == '您已添加过这个网站':
                        self.add_sitemap(url)
                        return False
                    print('验证失败')
                    input_code = self.driver.find_element_by_id('captcha')
                    input_code.clear()
            except ElementNotVisibleException:
                print('没有验证码')

    def set_item(self, select):
        print('选择领域')
        temp = WebDriverWait(self.driver, 1).until(EC.visibility_of(self.driver.find_element_by_xpath('//ul/li[18]/label')))
        if temp:
            for line in range(0, 25):
                checked = self.driver.find_element_by_id('check%s' % line).get_attribute('checked')
                if str(checked) == 'true':
                    self.driver.find_element_by_xpath('//ul/li[%s]/label' % (line + 1)).click()
            for line in select:
                self.driver.find_element_by_xpath('//ul/li[%s]/label' % (line + 1)).click()
            print('设置成功')
            time.sleep(1)
            self.driver.find_element_by_id('sub-attr').click()

    def get_code(self, code_type):
        self.driver.get_screenshot_as_file('screen.png')
        # 通过Image处理图像
        im = Image.open('screen.png')
        if code_type == 'add_url':
            im = im.crop((790, 790, 1000, 860))
        else:
            im = im.crop((730, 690, 900, 770))
        im.save('code.png')
        # 查询余额
        balance = self.yundama.balance()
        print('balance: %s' % balance)
        path = '/Users/hexiaotian/PycharmProjects/BDVerify/code.png'
        # 开始识别，图片路径，验证码类型ID，超时时间（秒），识别结果
        cid, code = self.yundama.decode(path, 2004, 20)
        print('cid: %s, result: %s' % (cid, code))
        return code

    def file_verify(self):
        print('开始下载验证文件')
        # 清空目录
        filename = os.listdir(self.upload_path)
        try:
            my_file = self.upload_path + filename[0]
            if os.path.exists(my_file):
                print('删除多余文件 %s' % filename[0])
                os.remove(self.upload_path + filename[0])
        except IndexError:
            pass
        WebDriverWait(self.driver, 5).until(EC.visibility_of(self.driver.find_element_by_xpath('//*[@id="file"]/p[2]/a')))
        self.driver.find_element_by_xpath("//dd[@id='file']/p[2]/a[1]").click()
        while True:
            filename = os.listdir(self.upload_path)
            try:
                name = filename[0]
                size = os.path.getsize(self.upload_path + name)
                if name.endswith('.html') and size > 5:
                    print('已找到下载文件' + name)
                    time.sleep(1)
                    break
            except IndexError:
                continue
        print('上传本地文件')
        while True:
            try:
                print('上传本地文件')
                self.sftp.put(self.upload_path + filename[0], self.remote_path + filename[0])
                time.sleep(2)
                print("上传文件成功 path: " + self.remote_path + filename[0])
                break
            except Exception:
                print("连接失败！ 再次重试上传")
                print("loading...")
                time.sleep(3)
                break
        state = True
        num = 1
        while state:
            if num > 5:
                raise TimeoutException
            files = self.sftp.listdir(self.remote_path)
            for name in files:
                print(name.strip('\n') + '  对比文件  ' + filename[0])
                if str(name) == str(filename[0]):
                    state = False
                    break
            print('等待上传...')
            time.sleep(1)
            num += 1
        print('上传成功！')
        my_file = self.upload_path + filename[0]
        if os.path.exists(my_file):
            print('删除本地下载文件')
            os.remove(self.upload_path + filename[0])
        self.driver.find_element_by_id('verifySubmit').click()
        while True:
            try:
                self.driver.find_element_by_id("dialog").click()
                print('验证成功')
                break
            except NoSuchElementException:
                print("正在验证中，请等待!")

    def add_sitemap(self, url):
        self.driver.get('https://ziyuan.baidu.com/linksubmit/index?site=http://www.%s/' % url)
        select = self.driver.find_element_by_xpath("//*[@id='submit-method-type']/li[@tab-value='sitemap']")
        self.driver.execute_script("arguments[0].scrollIntoView();", select)  # 拖动到可见的元素去
        select.click()
        text = self.driver.find_element_by_xpath('//*[@id="url-list"]/tbody/tr/td[2]').text
        if text == '暂无数据':
            select = self.driver.find_element_by_id("urls")
            select.click()
            select.send_keys('www.%s/sitemap.xml' % url)
            select = self.driver.find_element_by_xpath("//*[@id='captcha-img']/span")
            select.click()
            WebDriverWait(self.driver, 4).until(EC.visibility_of(self.driver.find_element_by_class_name('ml5')))
            while True:
                try:
                    verify = self.get_code('add_sitemap')
                    select = self.driver.find_element_by_id("captcha")
                    select.send_keys(verify)
                    self.driver.find_element_by_id('btn-submit').click()
                    xpath = '//*[@id="dialog-foot"]/button'
                    WebDriverWait(self.driver, 2).until(EC.visibility_of(self.driver.find_element_by_xpath(xpath)))
                    self.driver.find_element_by_xpath(xpath).click()
                    print('添加成功')
                    break
                except NoSuchElementException:
                    select = self.driver.find_element_by_id("captcha")
                    select.clear()
        else:
            print('已经存在sitemap.xml')


if __name__ == '__main__':
    BD = BDVerify()

    domain = linecache.getline('domain.txt', 1)
    item = linecache.getline('item.txt', 1)
    print(domain)
    print(item)

    # result = BD.add_url('bjgirls.cn')
    # print(result)
    # if result:
    #     BD.set_item([9, 17, 24])
    #     BD.file_verify()
