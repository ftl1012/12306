# coding: utf-8

import os
import time
import json
# 图片操作对象
from PIL import Image
# 将二进制文件转换为IO流输出
from io import BytesIO
import yundama

from selenium import webdriver
# 1. 导入模块
from selenium import webdriver
# 1> 等待对象模块
from selenium.webdriver.support.wait import WebDriverWait
# 2> 导入等待条件模块
from selenium.webdriver.support import expected_conditions as EC
# 3> 导入查询元素模块
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

browser = webdriver.Chrome("chromedriver")

# 12306是异步请求，所以使用selenium的显性等待方案
wait = WebDriverWait(browser, 10, 0.5)    # 创建等待对象

# 请求参数
linktypeid = 'dc'
fs = '上海,SHH'
ts = '成都,CDW'
date ='2019-02-03'
flag = 'N,N,Y'

# 请求URL：
# https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=上海&ts=北京&date=2019-02-03&flag=N,N,Y
base_url = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid={}&fs={}&ts={}&date={}&flag={}"
url = base_url.format(linktypeid, fs, ts, date, flag)

# 访问12306的列表页面
browser.get(url)

# 通过时间判定，选择点击预订
# 寻找tr标签中，属性id以ticket开头的数据
tr_list = wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//tr[starts-with(@id, 'ticket_')]")))  # 找到所有可见元素

for tr in tr_list:
    count = 0
    t_start = tr.find_element_by_class_name('start-t').text
    with open('start.txt', 'a') as f:
        f.write(t_start)

    # 判断时间是否在符合条件的范围内
    if count < 5 and t_start == "11:16":   # 这里以06:33为例
        tr.find_element_by_class_name('btn72').click()
        break
    else:
        count += 1
        continue


# 点击账号(注意因为是异步加载的所有需要显性等待)
# browser.find_element_by_link_text("账号登录").click()   # 因为还没有加载出来，因为是Ajax请求，所以要用until查找
wait.until(EC.visibility_of_element_located((By.LINK_TEXT, "账号登录"))).click()

# 打开json文件，
with open('account.json', 'r', encoding='utf-8') as f:
    account = json.load(f, encoding='utf-8')
    print(account['username'])



# 输入用户名和密码
j_username = browser.find_element_by_id('J-userName').send_keys(account['username'])
j_password = browser.find_element_by_id('J-password').send_keys(account['password'])


# 获取全屏图片
full_img_data = browser.get_screenshot_as_png()

# 计算截图位置
login_img_element = browser.find_element_by_id("J-loginImg")

# 获取截图元素对象
scale = 1.0
x1 = login_img_element.location["x"] - 155
y1 = login_img_element.location["y"] - 100
x2 = x1 + login_img_element.size["width"]
y2 = y1 + login_img_element.size["height"]
cut_info = (x1, y1, x2, y2)
print('cut_info', cut_info)

# 把全屏图片构建成全屏图片操作对象
full_img = Image.open(BytesIO(full_img_data))
# 通过截图信息对象截图图片
cut_img = full_img.crop(cut_info)
# 把图片保存到本地
cut_img.save('cut_img.png')
time.sleep(5)
# 利用云打码进行图片解析
result = yundama.decode('cut_img.png', '6701')
print('Image Decode:', result)

# 定义8个点击坐标点
positions = [
    (80, 140),
    (230, 140),
    (380, 140),
    (530, 140),
    (80, 280),
    (230, 280),
    (380, 280),
    (530, 280)
]

# 模拟点击坐标
for num in result:
    position = positions[int(num) - 1]
    # ActionChains 动作对象
    ActionChains(browser).move_to_element_with_offset(login_img_element,position[0] / 2,position[1] / 2).click().perform()
    print(position[0], position[1], "点击图片完成")
    time.sleep(5)


# 点击登录
browser.find_element_by_id("J-login").click()


# 点击选择人物
wait.until(EC.visibility_of_element_located((By.ID, "normalPassenger_1"))).click()

# 点击提交订单
browser.find_element_by_id('submitOrder_id').click()

time.sleep(2)
# 点击确认订单
wait.until(EC.visibility_of_element_located((By.ID, 'qr_submit_id'))).click()

print("抢票成功，请支付")



time.sleep(5)
browser.quit()