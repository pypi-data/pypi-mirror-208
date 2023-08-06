#!/usr/bin/python
# -*- coding: UTF-8 -*- 
"""   
@Author    : Gavin
@DateTime  : 2020/11/11 22:38
@Contact   : guowenwhy@foxmail.com

@Project   : TestToolBox
@File      : initUIEnv.py
@Describe  : 环境准备
————————————————————
@Version   : 0.1 
"""
# update   : 11-11 基础环境准备
# 1. todo 测试环境准备
# 2. 获取设备id 获取apk包名信息 - 准备启动apk 基础环境初始化
# ————————————————————
# update   : 12-09
# 1. adb 配置全局代理
# 2. 清除代理配置并重启
# ————————————————————
# update   : 2021/12/17
# 1. 区分 Taurus 和 Virgo 处理 设备环境初始化
# 2.
# ————————————————————
# update   :
# 1.
# ————————————————————


from loguru import logger

from TestToolBox.BaseUtility.adbShell import adbShell
from TestToolBox.Common.initConfig import CommonConfig

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


"""
# 原生 selenium remote-debug 调试
"""

LONG_WAIT, SHORT_WAIT = 2, 1


# @pytest.fixture()
def originDriver():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    chrome_driver = r"chromedriver.exe"
    driver = webdriver.Chrome(chrome_driver, chrome_options=chrome_options)
    # driver.get("https://www.baidu.com/")
    # print(driver.title)
    # driver.quit()
    return driver


"""
web 元素定位
"""


class myTour(CommonConfig):
    def __init__(self, tourGuide_file):
        super().__init__(tourGuide_file)
        self.tourPath = self.classData

    # 读取配置文件执行Tour导览
    def toursGuide(self, driver, guide_path, rootPath, tour_name=None, js_filename="demo_tourGuide.js", interval=0):
        guideContent = self.tourPath.finder(guide_path)
        self.tourPath.get("")
        driver.create_tour()
        for step, content in guideContent.items():
            # print(step, content)
            if content["selector"]:
                # 元素定位路径
                selector_path = rootPath.finder(content["selector"])
                content.update({"selector": selector_path})
                # print(f"debug: \n{content}")
            content.update({"name": tour_name})
            driver.add_tour_step(**content)
        driver.export_tour(filename=js_filename)
        driver.play_tour(interval=interval)

    # todo 定位到多个元素


# web 页面元素定位/操作 // 读取多种配置文件 进行元素定位 & 页面导览
class myLocator(CommonConfig):
    # 公共配置类 - 继承父类

    def __init__(self, elePath_file):
        super().__init__(elePath_file)
        self.elePath = self.classData
        # self.tourPath = myLocator.objectPath(guideMsg_file)

    """
    页面操作方法
    """

    # 聚焦浏览器窗口并全屏
    @classmethod
    def findWindow(cls, driver):
        driver.sleep(LONG_WAIT)
        driver.switch_to_default_window()
        logger.debug(f"initWeb - switch_to_default_window")
        driver.sleep(SHORT_WAIT)
        driver.maximize_window()
        driver.scroll_to_top()
        logger.debug(f"initWeb - maximize_window")


"""
Taurus 相关
"""


# 获取设备id
adb = adbShell()
# device_id = adb.get_device_id()


# todo app通用方法类
# 判断锁屏状态 解锁屏幕 - 黑屏/亮屏 解锁
def unlock_screen(driver):
    _step_tag = "unlock_screen -> "
    logger.debug(f"{_step_tag}判断屏幕锁定状态...")
    display_stat = adb.get_display_state()  # True 亮屏 / False 灭屏

    # 判断是否亮屏
    logger.debug(f"{_step_tag}屏幕开启状态: {display_stat}")
    driver.sleep(1)
    if display_stat:    # 亮屏
        # adb.send_keyevent(26)   # 按下电源键 - 关屏
        driver.screen_off()
        driver.sleep(1)
        logger.debug(f"{_step_tag}关闭屏幕,重新解锁")

    # adb.send_keyevent(26)   # 按下电源键 - 开屏
    driver.screen_on()
    driver.sleep(1)
    screen_unlocked = adb.get_screen_unlocked()  # True 锁定 / False 解锁
    logger.debug(f"{_step_tag}屏幕锁定状态: {screen_unlocked}")
    if screen_unlocked:   # 锁屏
        driver.sleep(2)
        driver.swipe_ext("up", 0.7, duration=0.1)
        driver.sleep(2)
        # 模拟器解锁
        # driver.swipe_points([[230, 1180], [230, 1400], [660, 1400]], 0.1)
        # 红米解锁
        driver.swipe_points([[270, 1340], [270, 1600], [800, 1600]], 0.1)
        driver.sleep(1)
        logger.debug(f"{_step_tag}已解锁屏幕")


# 通用导航验证 - 导航、页面元素验证
def commonNaviAssert(driver, target_ele, target_attr=""):
    d = driver
    _step_tag = "commonNavigator -> "
    
    targetEle = d.xpath(target_ele.xpath)
    logger.info(f"{_step_tag}验证元素正常：{target_ele.name}")
    assert targetEle, f"{_step_tag}ERROR INFO!\n未定位到元素 - {target_ele.xpath}"
    
    if target_attr:
        ele_attr = getattr(target_ele, target_attr)
        logger.debug(f"{_step_tag}验证元素属性 {target_attr}：{ele_attr}")
        if target_attr == "description":
            target_attr = "contentDescription"
        assert targetEle.info.get(target_attr) == ele_attr, f"{_step_tag}ERROR INFO!元素属性异常\n{targetEle.info}"


# 范围判定
def visible(driver, target_ele, _type="top", _board=0.15):   # -> True / False
    d = driver
    _step_tag = "visible -> "
    targetEle = d.xpath(target_ele.xpath)
    ele_range = targetEle.bounds  # (lx, ly, rx, ry)
    _width, _height = d.window_size()  # w, h
    # board = 0.15
    off_x = int(_width * _board)
    off_y = int(_width * _board)
    logger.debug(f"{_step_tag}验证元素位于可见范围 {ele_range}：{_type} 边界-{_board}; {off_x, off_y, _width - off_x, _height - off_y}")
    _type = _type.lower()
    if _type == "left":
        if ele_range[0] <= off_x:
            logger.debug(f"{_step_tag}Left Line OutRange!{ele_range[0]} !! {off_x}")
            return False
    if _type == "top":
        if ele_range[1] <= off_y:
            logger.debug(f"{_step_tag}Top Line OutRange!{ele_range[1]} !! {off_y}")
            return False
    if _type == "right":
        if ele_range[2] >= _width - off_x:
            logger.debug(f"{_step_tag}Right Line OutRange!{ele_range[2]} !! {_width - off_x}")
            return False
    if _type == "bottom":
        if ele_range[3] >= _height - off_y:
            logger.debug(f"{_step_tag}Bottom Line OutRange!{ele_range[3]} !! {_height - off_y}")
            return False
    return True


# 验证元素在可见范围内 0.15 * WindowRange
def commonVisibleAssert(driver, target_ele, _type="upDown", _board=0.15):
    d = driver
    _step_tag = "commonVisibleAssert -> "

    logger.debug(f"{_step_tag}验证元素位于可见范围 {target_ele.name}：边界 {_type}: {_board}")
    if _type == "upDown":
        assert visible(d, target_ele, "top"), f"{_step_tag}Top Point OutRange!"
        assert visible(d, target_ele, "bottom"), f"{_step_tag}Bottom Point OutRange!"

    elif _type == "leftRight":
        assert visible(d, target_ele, "left"), f"{_step_tag}Left Point OutRange!"
        assert visible(d, target_ele, "right"), f"{_step_tag}Right Point OutRange!"

    elif _type == "box":
        assert visible(d, target_ele, "left"), f"{_step_tag}Left Point OutRange!"
        assert visible(d, target_ele, "top"), f"{_step_tag}Top Point OutRange!"
        assert visible(d, target_ele, "right"), f"{_step_tag}Right Point OutRange!"
        assert visible(d, target_ele, "bottom"), f"{_step_tag}Bottom Point OutRange!"
    else:
        raise Exception(f"{_step_tag}ERROR INFO!\n元素可见范围验证类型 _type 错误！e.g upDown, leftRight, box")

    # {'text': 'My Profile', 'focusable': 'false', 'enabled': 'true', 'focused': 'false', 'scrollable': 'false', 'selected': 'false', 'className': 'android.widget.TextView', 'bounds': {'left': 58, 'top': 172, 'right': 953, 'bottom': 287}, 'contentDescription': '', 'longClickable': 'false', 'packageName': 'com.fiture.taurus.international', 'resourceName': 'com.fiture.taurus.international:id/tv_my', 'resourceId': 'com.fiture.taurus.international:id/tv_my', 'childCount': 0}


# 目标定位偏移点击 - 已有方法
def offsetClick(driver, target_ele, target_attr="", offset_x=0, offset_y=0):
    d = driver
    _step_tag = "offsetClick -> "
    commonNaviAssert(driver, target_ele, target_attr)
    targetEle = d.xpath(target_ele.xpath).info
    logger.debug(f"{_step_tag}验证元素属性\n{targetEle}")
    # assert targetEle.info.get("clickable"), f"{_step_tag}ERROR INFO!元素不可点击\n{targetEle.info}"
    left_x = targetEle.get('bounds').get('left')
    top_y = targetEle.get('bounds').get('top')
    logger.debug(f"{_step_tag}定位元素横纵坐标 {left_x}:{top_y}：偏移量 {offset_x}:{offset_y}")
    d.click(left_x + offset_x, top_y + offset_y)


# centerTarget 居中目标 # ver 1.0
def centerTarget_v1(driver, target_ele, target_attr=""):
    d = driver
    _step_tag = "centerTargetEle-ver1.0 -> "

    # d(range_ele).scroll.to(target_ele.xpath)
    commonNaviAssert(driver, target_ele, target_attr)
    targetEle = d.xpath(target_ele.xpath).info.get('bounds')
    left_x = targetEle.get('left')
    top_y = targetEle.get('top')
    total_x, total_y = d.window_size()
    logger.debug(f"{_step_tag}滑动居中元素 {target_ele.name} 坐标 {left_x}:{top_y}")
    # d.swipe(left_x, top_y, total_x, total_y, 0.2)
    d.swipe_points([[left_x, top_y], [total_x // 2, total_y // 2]], 0.1)

    if 0.1*total_x < left_x or 0.9*total_x > left_x:
        d.swipe_ext("up", 0.3)
        print("swipe", left_x, top_y, left_x, total_y//3)
        d.swipe(left_x, top_y - total_x*0.3, left_x, total_y//3)
    else:
        # d.swipe_points([[x, y], [x, _y//3]], 0.1)
        d.swipe(left_x, top_y, left_x, total_y//3)


# centerTarget - common 上下边界限定
def commonEdge(driver, *coordinate):       # -> x, y
    d = driver
    x, y = coordinate
    w, h = d.window_size()
    if y > h - 156:    # Tab 导航栏高度
        y = h - 157
        logger.debug(f"commonEdge -> 低于导航栏, 更新坐标{x, y}")
    return x, y


# centerTarget - swipe center 拖动元素至中心位置
def swipe2Center(driver, target_ele, _diff=100):
    d = driver
    _step_tag = "swipe2Center 将元素居中 -> "
    w, h = d.window_size()
    center_x = int(w // 2)
    center_y = int(h // 2)
    range_w = range(center_x - _diff*2, center_x + _diff*2)
    range_h = range(center_y - _diff*7, center_y + _diff*7)
    # 滑动元素坐标至屏幕中心区域 540 [340, 640], 860 []
    # targetEle = d.xpath(target_ele.xpath)  # 位置变化 xpath 变化 !!!
    targetEle = d(**autoField(target_ele))
    ele_x, ele_y = targetEle.center()
    ele_x, ele_y = int(ele_x), int(ele_y)
    logger.debug(f"{_step_tag}判断元素是否居中: X:{ele_x}, {range_w} Y:{ele_y}, {range_h}")
    while ele_x not in range_w or ele_y not in range_h:
        logger.debug(f"{_step_tag}元素未居中 X:{ele_x}, {range_w} Y:{ele_y}, {range_h}\n循环滑动元素...")
        if ele_x not in range_w:
            flex_x, flex_y = commonEdge(d, ele_x, ele_y)
            # d.swipe(flex_x, flex_y, center_x, flex_y)
            d.swipe_points([[flex_x, flex_y], [center_x, flex_y]], 0.1)
            d.sleep(0.7)    # 取消连击
        if ele_y not in range_h:
            flex_x, flex_y = commonEdge(d, ele_x, ele_y)
            # d.swipe(flex_x, flex_y, flex_x, center_y)
            d.swipe_points([[flex_x, flex_y], [flex_x, center_y]], 0.1)
            d.sleep(0.7)    # 取消连击
        # ele_x, ele_y = d.xpath(target_ele.xpath).center()    # # 位置变化 xpath 变化 !!!
        ele_x, ele_y = d(**autoField(target_ele)).center()
        ele_x, ele_y = int(ele_x), int(ele_y)
        logger.debug(f"{_step_tag}更新元素中心坐标: X:{ele_x}, {range_w} Y:{ele_y}, {range_h}")
    logger.info(f"{_step_tag}已居中元素: {targetEle.bounds()}")


# centerTarget - d(**fields) 自动传参
def autoField(target_ele):
    _step_tag = "autoField 自动传参 -> "
    _field = ["index", "text", "description", "resourceId"]
    result = {}
    for key, val in target_ele.items():
        if key in _field:
            result[key] = val
    logger.debug(f"{_step_tag}遍历元素定位属性结果： {result}")
    if result:
        return result
    else:
        raise Exception(f"{_step_tag}ERROR INFO!\n遍历元素 {target_ele} 定位属性为空！")


# ver 2.0 复用集成方法
def centerTarget(driver, target_ele, small_range=None, big_range=None, _board=0.15):
    d = driver
    if small_range is None:
        small_range = d(scrollable=True)
    else:
        small_range = d(**autoField(small_range))
    if big_range is None:
        big_range = d(scrollable=True)
        
    _step_tag = "centerTargetEle-ver2.0 -> "
    # 1 - 全屏滚动 找到模块
    # d(scrollable=True).scroll.to(resourceId=target_ele.resourceId)
    # 目标范围内 查找内容
    # test_element = {"text": "", "resourceId": ""}
    # d(**test_element).scroll.to(resourceId=target_ele.resourceId)
    logger.info(f"{_step_tag}整页滑动至找到元素...")
    if not big_range.scroll.to(**autoField(target_ele)):
        raise Exception(f"{_step_tag}ERROR INFO!\n整页滑动未找到元素!")
    # targetEle = d.xpath(target_ele.xpath)
    # ele_range = targetEle.bounds        # (lx, ly, rx, ry)
    # _width, _height = d.window_size()    # w, h
    # _width, _height = int(_width), int(_height)
    # logger.debug(f"{_step_tag}验证元素位于可见范围 {ele_range}：边界-{_board}; {_height * _board, _height * (1 - _board)}")
    # 模块居中
    if not visible(d, target_ele, "bottom"):
        logger.debug(f"{_step_tag} 向上滑动,上移元素")
        d.swipe_ext("up", 1)
    if not visible(d, target_ele, "top"):
        logger.debug(f"{_step_tag} 向下滑动,下移元素")
        d.swipe_ext("down", 0.5)
    if not visible(d, target_ele, "left"):
        logger.debug(f"{_step_tag} 向右滑动,右移元素")
        small_range.scroll.horiz.backward()
    if not visible(d, target_ele, "right"):
        logger.debug(f"{_step_tag} 向左滑动,左移元素")
        small_range.scroll.horiz.forward()
    # new_ = targetEle.bounds
    # d.swipe(new_[0], new_[1], new_[0],)
    # 滑动居中
    swipe2Center(d, target_ele)


if __name__ == '__main__':
    pass

    # get_devices()
    # os.chdir("../")
    # print(os.getcwd())

    # print(screen_unlocked)

    # adb.send_keyevent(26)

    # unlock_screen()

