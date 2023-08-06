# -*- coding: UTF-8 -*-

import pyautogui
import pyperclip


# 模拟输入法操作
def insert(sub):
    """
    :param sub: 需要打印的内容
    :type sub: str
    :return:
    :rtype:
    """
    pyperclip.copy(sub)
    pyautogui.hotkey('ctrl', 'v')


