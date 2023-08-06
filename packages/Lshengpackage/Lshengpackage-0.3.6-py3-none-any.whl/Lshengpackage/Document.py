# -*- coding: UTF-8 -*-


import os

import pandas as pd

file_name_list = []  # 文件夹下截图的名称


# 删除文件夹下所有文件
def del_files(dir_path):
    """
    :param dir_path: 文件夹路径
    :type dir_path:  str
    :return:
    :rtype:
    """
    if os.path.isfile(dir_path):
        try:
            os.remove(dir_path)  # 这个可以删除单个文件，不能删除文件夹
        except BaseException as e:
            return e
    elif os.path.isdir(dir_path):
        file_lis = os.listdir(dir_path)
        for file_name in file_lis:
            # if file_name != 'wibot.log':
            tf = os.path.join(dir_path, file_name)
            del_files(tf)
    # print('ok')


# 获取文件夹下所有文件名
def file_name(file_path):
    """
    :param file_path:  文件夹路径
    :type file_path:  str
    :return:
    :rtype:
    """
    filenames = os.listdir(file_path)
    del file_name_list[:]
    for i in filenames:
        scr_name = int(i.split('.')[0])
        file_name_list.append(scr_name)


# 检测路径是否存在，不存在则创建路径
def mk_f(path):
    """
    检测路径是否存在，不存在则创建路径
    """
    pa = os.path.exists(path)
    if pa is not False:
        pass
    else:
        os.mkdir(path=path)


# xls_转_xlsx程序，文件夹为程序exc下，转换后自动读取
def xls_to_xlsx(path, f_name , sheet_name):
    """
    excel  .xls 后缀 改成 .xlsx 后缀
    path 文件夹路径
    f 读取文件的文件名
    """
    file_name_be, suff = os.path.splitext(f_name)  # 路径进行分割，分别为文件路径和文件后缀
    # print(file_name_be, suff)
    if suff == '.xls':
        # ui.printf('将对{}文件进行转换...'.format(f_name))
        # print(path + '/' + f)
        data = pd.DataFrame(pd.read_excel(path + '/' + f_name, sheet_name=sheet_name))  # 读取xls文件
        data.to_excel(os.getcwd() + '/exc/' + file_name_be + '.xlsx', sheet_name=sheet_name, index=False)  # 格式转换
        return file_name_be + '.xlsx'
    else:
        pass