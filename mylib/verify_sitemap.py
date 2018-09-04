# -*- coding=utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

file1 = open("C:/Users/Administrator/Desktop/www_urls_all_5.txt", "r+")


def login(driver):
    driver.get("https://ziyuan.baidu.com/login/index?u=/?castk=LTE%3D")
    print("login success !!")
    return driver


def pase(line, driver):
    driver.get("https://ziyuan.baidu.com/linksubmit/index?site=http%3A%2F%2F" + line + "/")
    select = driver.find_element_by_xpath("//*[@id='submit-method-type']/li[@tab-value='sitemap']")
    driver.execute_script("arguments[0].scrollIntoView();", select)  # 拖动到可见的元素去
    select.click()
    select = driver.find_element_by_id("urls")
    select.click()
    select.send_keys(line + '/sitemap.xml')
    select = driver.find_element_by_xpath("//*[@id='captcha-img']/span")
    select.click()
    verify = input("输入验证码：")
    select = driver.find_element_by_id("captcha")
    print(verify.__len__())
    select.send_keys(verify[0:8])
    driver.find_element_by_id('btn-submit').click()
    time.sleep(3)


driver = webdriver.Chrome()  # 打开浏览器
# driver.maximize_window()
driver = login(driver)
num = 1
while True:
    line = file1.readline().split('\n', 1)[0]
    print('当前提交网站为' + line + '当前为第' + str(num) + "行")
    num += 1
    if line == '':
        break
    pase(line, driver)
    print("程序完成")
