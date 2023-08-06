# !/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import sys

import pyautogui
from Lshengpackage.simulate.mock_findPic import find_image

# 加载
def load(fol_path, target_path, target):
    """
        :param img: 循环等待的值
        :type img: img
        :return: 鼠标(1,1),返回 'N'
        :rtype:
        """
    while True:
        iocn = find_image(fol_path, target_path, target)
        if iocn is not None:
            return iocn
        x, y = pyautogui.position()
        if x & y == 0:
            sys.exit()
            # 暂时先这样结束进程
        else:
            pass


def load_click(fol_path, target_path, target):
    """
    加载点击
    """
    iocn = load(fol_path, target_path, target)
    if iocn is not None:
        pyautogui.click(iocn[0], iocn[1])
        return True
    else:
        return False
