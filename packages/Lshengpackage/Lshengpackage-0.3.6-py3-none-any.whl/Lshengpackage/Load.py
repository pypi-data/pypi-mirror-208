# !/usr/bin/env python
# -*- coding: UTF-8 -*-

import pyautogui
from Lshengpackage.simulate.pc.find_pic import screen_shot, find_image

# 加载
def load(img):
    """
        :param img: 循环等待的值
        :type img: img
        :return: 鼠标(1,1),返回 ''
        :rtype:
        """
    while True:
        screen_shot()
        iocn = find_image(img)
        if iocn is not None:
            return iocn
        x, y = pyautogui.position()
        if x & y == 1:
            return 'N'


def load_click(img):
    while True:
        screen_shot()
        iocn = find_image(img)
        if iocn is not None:
            pyautogui.click(iocn[0], iocn[1])
            return iocn
        x, y = pyautogui.position()
        if x & y == 1:
            return 'N'
