# -*coding:utf-8 -*-
# !/usr/bin/env python
import pickle
from Lshengpackage.tools.Loading import load_click, load, insclick
from Lshengpackage.simulate.mock_findPic import find_image
from PIL import Image


def start_picdata(pypath):
    global image_data
    with open(pypath, 'rb') as f:
        image_data = pickle.load(f)


def read_img(path, img_name):
    # 读取py的图片并缓存为临时文件
    img_data = image_data[img_name][0]
    img = Image.new(mode='RGB', size=(img_data['width'], img_data['height']))
    img.putdata(img_data['pixel_values'])
    img.save(path + 'public.png')


def refind_image(fol_path, path, img_name, _system=None, int_x1=-1, int_y1=None, int_x2=None, int_y2=None):
    read_img(path, img_name)
    pub = find_image(fol_path, path + 'public.png', _system, int_x1, int_y1, int_x2, int_y2)
    if pub is not None:
        return pub


def refiloadclick_image(fol_path, path, img_name, _system):
    read_img(path, img_name)
    pub = load_click(fol_path, path + 'public.png', _system)  # 退出当前页再找
    if pub is True:
        return True
    else:
        return False


def refiload_image(fol_path, path, img_name, _system):
    read_img(path, img_name)
    pub = load(fol_path, path + 'public.png', _system)  # 退出当前页再找
    if pub is not None:
        return pub


def refiinsclick_image(fol_path, path, img_name, _system):
    read_img(path, img_name)
    pub = insclick(fol_path, path + 'public.png', _system)  # 退出当前页再找
    if pub is True:
        return True
    else:
        return False
