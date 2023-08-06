from time import sleep
import os
import sys
import cv2
import pyautogui


# 截图
def screen_shot():
    sleep(0.1)
    pyautogui.screenshot('pic/sre.png')


# 当前页面找图,找到匹配对象位置中心点
def find_image(target):
    """
    在当前页面上找目标图片坐在坐标，返回中心坐标 (x,y)
    :param driver:
    :param target: 例：../img/test.png
    :return:
    """
    
    # 获取当前页面的截图
    source_path = os.path.join('pic/sre.png')
    # driver.save_screenshot(source_path)
    # ImageGrab.grab().save(source_path)
    
    # 获取目标图片的存放路径
    target_path = os.path.join('pic/' + target)
    
    source_image = cv2.imread(source_path)
    target_image = cv2.imread(target_path)
    
    # 使用 TM_CCOEFF_NORMED 获取目标图片与原图片的每个点的匹配度
    result = cv2.matchTemplate(source_image, target_image, cv2.TM_CCOEFF_NORMED)
    
    # 找出匹配度最高的点和最低的点，并返回对应的坐标
    match_result = cv2.minMaxLoc(result)
    
    if match_result[1] > 0.9:  # 匹配度大于90%，视为匹配成功
        pos_start = cv2.minMaxLoc(result)[3]  # 获取匹配成功后的起始坐标
        
        # 计算匹配对象的中心位置坐标
        x = int(pos_start[0]) + int(target_image.shape[1]) / 2
        y = int(pos_start[1]) + int(target_image.shape[0]) / 2
        if sys.platform == 'darwin':
            return x / 2, y / 2
        else:
            return x, y
    else:
        return None


def compare_image(target):
    screen_shot()
    im = find_image(target)
    if im is not None:
        return im
