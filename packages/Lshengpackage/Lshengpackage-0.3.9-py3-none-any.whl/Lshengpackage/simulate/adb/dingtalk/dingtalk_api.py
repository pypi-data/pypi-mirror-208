# -*- coding: UTF-8 -*-
import os
from time import sleep
from Lshengpackage.simulate.adb.Command_adb import command
from Lshengpackage.simulate.adb.re_Pic import refind_image, refiinsclick_image, refiloadclick_image, refiload_image


# 检测当前连接状态
def connect_status_api():
    state = os.popen('adb get-state').read()  # ddddddddddd
    if state[0:7] == 'unknown':
        print('未检测到连接设备')
        return False
    elif state[0:6] == 'device':
        print('设备连接正常')
        return True
    else:
        print('设备无响应,请重启设备尝试')


# 连接adb
def connect_api(ip):
    connect = os.system('adb connect {}'.format(ip))
    if connect == 0:
        txt = '连接设备{},成功'.format(ip)
        # print(txt)
        return txt


# 检测dingding当前界面
def ding_current_api(fol_path, path, _system):
    sleep(0.1)
    if refind_image(fol_path, path, 'is_msg', _system) is not None:
        print('******当前页面为消息页******')
        return '消息页'
    elif refind_image(fol_path, path, 'is_tooge', _system) is not None:
        print('******当前页面为协作页******')
        return '协作页'
    elif refind_image(fol_path, path, 'is_work', _system) is not None:
        print('******当前页面为办公页******')
        return '办公页'
    elif refind_image(fol_path, path, 'is_iph', _system) is not None:
        print('******当前页面为通讯页******')
        return '通讯页'
    elif refind_image(fol_path, path, 'is_my', _system) is not None:
        print('******当前页面为个人页******')
        return '个人页'
    elif refind_image(fol_path, path, 'is_exa', _system) is not None:
        print('******当前页面为自查页,立即返回主程序******')

        refiinsclick_image(fol_path, path, 'tureok', _system)
        refiinsclick_image(fol_path, path, 'exit', _system)
        sleep(0.1)
        ding_current_api(fol_path, path, _system)
    elif refind_image(fol_path, path, 'is_answer', _system) is not None:
        print('******当前页面为答题页,立即返回主程序******')
        refiinsclick_image(fol_path, path, 'tureok', _system)
        refiloadclick_image(fol_path, path, 'exit', _system)
        sleep(0.1)
        ding_current_api(fol_path, path, _system)


# 打开应用接口 #答题 op_answer.png 自查 op_exaself.png
def open_app_api(fol_path, path, _system, op_name):  # op_name op的名
    xy = refiinsclick_image(fol_path, path, 'is_work', _system)
    if xy is False:
        refiinsclick_image(fol_path, path, 'work', _system)
    else:
        pass
    op_answer = refiinsclick_image(fol_path, path, op_name, _system)
    if op_answer is False:
        is_work = refind_image(fol_path, path, 'is_work', _system)
        if is_work is not None:
            command().swip_work(int(is_work[0]), int(is_work[1] - 400), int(is_work[0]), int(is_work[1]))
    else:
        op_answer = refiinsclick_image(fol_path, path, op_name, _system)
        print('{}页已打开,持续更近中'.format(op_name))
        return True
    for i in range(2):
        op_answer = refind_image(fol_path, path, op_name, _system)
        if op_answer is False:
            sleep(0.1)
            is_work = refind_image(fol_path, path, 'is_work', _system)
            command().swip_work(int(is_work[0]), int(is_work[1] - 100), int(is_work[0]), int(is_work[1] - 500))
        else:
            op_answer = refiinsclick_image(fol_path, path, op_name, _system)
            print('{}页已打开,持续更近中'.format(op_name))
            return True


# 安全答题程序执行程序接口
def do_answer_api(fol_path, path, _system):
    refiload_image(fol_path, path, 'do_answer', _system)
    sleep(0.5)

    do_fi_answer = refind_image(fol_path, path, 'do_fi_answer', _system)
    if do_fi_answer is not None:  # 处理上次记忆时间
        pass
    else:
        refiloadclick_image(fol_path, path, 'do_answer', _system)
    refiinsclick_image(fol_path, path, 'do_fi_answer', _system)
    sleep(0.1)

    lo = refiload_image(fol_path, path, 'do_fi_ti_answer', _system)  # 加载
    v = 0
    for i in range(5):
        v += 1
        refiinsclick_image(fol_path, path, 'push', _system)  # 加载

        _upup(fol_path, path, _system, a=v)

        answer(fol_path, path, _system)
    refiloadclick_image(fol_path, path, 'update', _system)
    refiload_image(fol_path, path, 'answer_over', _system)
    print('答题成功！！！')
    refiinsclick_image(fol_path, path, 'exit', _system)  # 加载
    refiloadclick_image(fol_path, path, 'ose', _system)


def _upup(fol_path, path, _system, a):
    while True:

        sh = refiload_image(fol_path, path, 'shouqi', _system)  # 加载
        command().swip_work(int(sh[0]), int(sh[1]), int(sh[0]), int(sh[1] - 100))

        pu = refind_image(fol_path, path, 'push', _system)  # 加载
        if pu is not None:
            return True
        else:
            if a == 5:
                command().swip_work(int(sh[0]), int(sh[1]), int(sh[0]), int(sh[1] - 500))
                return True


def answer(fol_path, path, _system):
    for i in ['A', 'B', 'C', 'D']:

        select = refind_image(fol_path, path, 'select', _system, int_x1=0, int_y1=540, int_x2=1920,
                              int_y2=1080)
        command().tap_work(int(select[0]), int(select[1] + 40))
        refiloadclick_image(fol_path, path, '{}'.format(i), _system)  # 加载
        sleep(0.2)

        yesok = refind_image(fol_path, path, 'yesok', _system, int_x1=0, int_y1=540, int_x2=1920,
                             int_y2=1080)
        if yesok is not None:
            return True


# 每日安全自查程序接口
def do_checkself_api(fol_path, path, _system):
    refiloadclick_image(fol_path, path, 'city', _system)
    refiloadclick_image(fol_path, path, 'jiujiang', _system)
    refiloadclick_image(fol_path, path, 'district', _system)
    refiloadclick_image(fol_path, path, 'lianxiqu', _system)
    refiloadclick_image(fol_path, path, 'attribute', _system)
    refiloadclick_image(fol_path, path, 'safeguard', _system)
    refiloadclick_image(fol_path, path, 'specialized', _system)
    refiloadclick_image(fol_path, path, 'guest', _system)
    te = refiload_image(fol_path, path, 'temp', _system)
    command().tap_work(int(te[0]), int(te[1] + 20))

    os.popen('adb shell input text 36')  # 输入文本
    while True:
        command().swip_work(int(te[0]), int(te[1]), int(te[0]), int(te[1] - 200))
        for i in range(5):
            ye = refiinsclick_image(fol_path, path, 'yes', _system)
            if ye is False:
                break
        sleep(0.1)

        ye = refind_image(fol_path, path, 'saferope', _system)
        if ye is not None:
            break
    refiloadclick_image(fol_path, path, 'update', _system)
    refiload_image(fol_path, path, 'selfsafe_over', _system)
    print('自查成功！！！')
    refiinsclick_image(fol_path, path, 'exit', _system)
