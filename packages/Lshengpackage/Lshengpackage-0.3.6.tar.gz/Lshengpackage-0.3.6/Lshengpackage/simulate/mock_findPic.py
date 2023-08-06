from time import sleep
import os
import sys
import cv2
import pyautogui
from adb.Command_adb import command
from PIL import Image


# 截图
def screen_shot(fol_path,scr_name):
    sleep(0.1)
    pyautogui.screenshot('{}{}.png'.format(fol_path,scr_name))


# 当前页面找图,找到匹配对象位置中心点
def find_image(fol_path, target_path, target,src_name='src', _system=None, int_x1=0, int_y1=None, int_x2=None, int_y2=None):
    """
    在当前页面上找目标图片坐在坐标，返回中心坐标 (x,y)
    :param path:
    :param target: 例：../img/test.png
    :return:
    """
    if _system == 'hwnd':  # hwnd暂时没更新进来
        pass
    elif _system == 'adb':  # android adb 截图
        cut = command()
        cut.cut_scr(target, fol_path)
    elif _system is None:  # pyautogui 截图
        screen_shot(fol_path,src_name)
    # 获取当前页面的截图
    source_path = os.path.join('{}{}.png'.format(fol_path,src_name))
    if int_x1 == 0:
        img = Image.open(source_path)
        code_image = img.crop((int_x1, int_y1, int_x2, int_y2))
        code_image.save(source_path)  # 原地址重写

    # 获取目标图片的存放路径
    target_path = os.path.join(target_path + target)

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
            if int_x1 == 0:
                return x / 2, y / 2
            else:
                return (x + int_x1) / 2, (y + int_y1) / 2
        else:
            if int_x1 == 0:
                return x, y
            else:
                return (x + int_x1), (y + int_y1)
    else:
        return None


