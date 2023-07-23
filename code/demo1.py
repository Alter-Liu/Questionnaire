# -*- coding: utf-8-*-
# 原文链接：https://blog.csdn.net/knighthood2001/article/details/120175929
import random
import sys
from selenium import webdriver
import time
from selenium.webdriver import ActionChains
import schedule

# 用来表示需要填写的问卷数目
target = 75
# 计数器，用来计算完成次数
count = 0
# 定义driver
global driver


# 为了实现不同题目的结果有差异化，使用此函数来确定每题的结果概率，同时简化run函数
def p_r(i, len_a=4):
    if i == 1 or i == 2 or i == 5:
        b = random.random()
        if b <= 0.8:
            return 1
        else:
            return 2
    elif i == 3 or i == 4 or i == 6:
        b = random.random()
        if b <= 0.65:
            return 1
        else:
            return 2
    elif i == 14:
        b = random.random()
        if b <= 0.4:
            # 选A的概率为百分之40
            b = 1
        elif b <= 0.7:
            b = 2
        elif b <= 0.9:
            b = 3
        else:
            b = 4
        return b
    else:
        # 从2到选项个数中选择一个数据，用于确定需要选择几个选项
        b = random.randint(2, len_a)
        # 从1到选项个数中随机选择b个，代表要选择的项
        q = random.sample(range(1, len_a+1), b)
        if i == 7:
            if b <= 3:
                q.append(3)
            else:
                q.append(5)
        if i == 9:
            if b <= 3:
                q.append(4)
            else:
                q.append(5)
        if i == 11:
            if b <= 3:
                q.append(3)
        if i == 16:
            if b <= 3:
                q.append(1)
            elif b == 4:
                q.append(4)
        return q


def sum_print():
    global count
    count += 1
    print("第{}次运行".format(count))


def get_track(distance):  # distance为传入的总距离
    # 移动轨迹
    track = []
    # 当前位移
    current = 0
    # 计算间隔
    t = 0.2
    # 初速度
    v = 0
    while current < distance:
        # 加速度
        a = 50
        v0 = v
        # 当前速度
        v = v0 + a * t
        # 移动距离
        # move = v0 * t + 1 / 2 * a * t * t
        move = v0 * t + a * t
        # 当前位移
        current += move
        # 加入轨迹
        track.append(round(move))
    return track  # list 返回的是整个滑动条的多个焦点，可以模拟鼠标的缓慢滑动


def move_to_gap(slider, tracks):  # slider是要移动的滑块,tracks是要传入的移动轨迹
    ActionChains(driver).click_and_hold(slider).perform()
    for x in tracks:
        ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
    time.sleep(0.1)
    ActionChains(driver).release().perform()


def run():
    global driver
    url = 'https://www.wjx.cn/vm/wrN6PZN.aspx#'
    # 躲避智能检测
    option = webdriver.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=option)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                           {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
                            })
    driver.get(url)
    sum_print()
    # 总共有17个题目
    i = 1
    while i <= 17:
        base_xpath1 = '//*[@id="div{}"]'.format(i)
        base_xpath2 = base_xpath1 + '/div[2]/div'
        a = driver.find_elements_by_xpath(base_xpath2)
        # print(len(a)),用于输出题目的选项个数
        # 前六题
        if i <= 6 or i == 14:
            # 从1到4中随机选择一个整数
            b = p_r(i)
            # 点击对应的选项
            driver.find_element_by_css_selector('#div{} > div.ui-controlgroup > div:nth-child({})'.format(i, b)).click()
            # 应对填空题的情况，但自己做就不建议
            # time.sleep(1)
            # 这里你可以每隔一段时间更改send_keys中的内容，也可以将答案写出来，然后随机选择哪个选项
            # driver.find_element_by_css_selector('#tqq6_4').send_keys('QQ群和微信群')
        else:
            q = p_r(i, len(a))
            # sort函数表示将列表排序，如果未加参数表示从小到大排列，理论不排也行？先选那个后选哪个的区别
            # q.sort()
            for r in q:
                driver.find_element_by_css_selector(
                    '#div{} > div.ui-controlgroup > div:nth-child({})'.format(i, r)).click()
        i += 1

    time.sleep(0.5)
    # 点击提交
    driver.find_element_by_xpath('//*[@id="ctlNext"]').click()
    # 出现点击验证码验证
    time.sleep(1)
    # 下面这个英文注释用来解决Pycharm 提示错误类型太宽泛
    # 下面这个代码块用于解决填写过程中偶尔会出现一个弹窗说请滑动滑块进行验证，此时需要点击确认
    # noinspection PyBroadException
    try:
        driver.find_element_by_xpath('//*[@id="layui-layer1"]/div[3]/a').click()
    except:
        pass
    time.sleep(1)

    # 部分情况下没有验证码验证，所以需要使用try，避免因为报错而停止运行
    # noinspection PyBroadException
    try:
        driver.find_element_by_xpath('//*[@id="alert_box"]/div[2]/div[2]/button').click()
    except:
        pass
    time.sleep(0.5)
    # noinspection PyBroadException
    try:
        driver.find_element_by_xpath('//*[@id="rectMask"]').click()
    except:
        pass
    time.sleep(4)
    # noinspection PyBroadException
    try:
        huakuai = driver.find_element_by_css_selector('#nc_1_n1z')
        move_to_gap(huakuai, get_track(328))
    except:
        pass
    finally:
        # 关闭页面
        handles = driver.window_handles
        driver.switch_to.window(handles[0])
        time.sleep(1)
        # 刷新页面（可能不需要）
        # driver.refresh()
        # 关闭当前页面，如果只有一个页面，则也关闭浏览器
        driver.close()
        # 到指定数目问卷时退出
        if count == target:
            sys.exit()


# 按时运行run函数
schedule.every(1).seconds.do(run)

while True:
    schedule.run_pending()
