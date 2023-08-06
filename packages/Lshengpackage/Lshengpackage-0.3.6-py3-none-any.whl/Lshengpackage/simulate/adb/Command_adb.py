# -*coding:utf-8 -*-
# !/usr/bin/env python

from PIL import ImageFile
from PIL import Image
import os


class command:
    def dev(self):
        # 查看当前链接设备
        os.system('adb devices')

    def log(self):
        # 查看日志
        os.system('adb logcat')

    def kill(self):
        # 结束adb服务
        os.system('adb kill-server')

    def star(self):
        # 开始adb服务
        os.system('adb start-server')

    def install(self, apk_name):
        # 安装软件
        os.system('adb install -r {}.apk'.format(apk_name))

    def uninstall(self, apk_name):
        # 卸载
        os.system('adb uninstall {}.apk'.format(apk_name))

    def up(self, file_name, path_phone):
        # 上传SDCard/../..手机端路径
        os.system('adb push {} {}'.format(file_name, path_phone))

    def down(self, file_name):
        # 下载
        os.system('adb uninstall {}'.format(file_name))

    def scr(self, path_pic_name):
        # 屏幕截图到手机根目录
        os.system('adb shell screencap -p /sdcard/{}.png'.format(path_pic_name))

    def video_scr(self, video_name):
        # 录屏，默认mp4格式
        os.system('adb shell screenrecord /sdcard/{}.mp4'.format(video_name))

    def cut_scr(self, path_pic_name, path):
        # 屏幕截图到本地
        # pic_name:屏幕截图生成地址+名称，默认为手机的根目录,默认的来
        # path为文件夹目录下
        self.scr(path_pic_name)
        os.system("adb pull /sdcard/{} {}{}.png".format(path_pic_name, path, path_pic_name))
        ImageFile.LOAD_TRUNCATED_IMAGES = True

    def spec_scr(self, pic_name, path, int_x1, int_y1, int_x2, int_y2):
        """
        指定截图保存
        左上角的点到右下角的点
        """
        self.cut_scr(pic_name, path)
        img = Image.open(path + pic_name)
        # (4)将图片验证码截取
        code_image = img.crop((int_x1, int_y1, int_x2, int_y2))
        code_image.save(path + pic_name)  # 原地址重写

    def tap_work(self, x, y):
        """
        模拟点击操作
        """
        os.system('adb shell input tap {} {}'.format(x, y))

    def swip_work(self, x, y, x2, y2):
        """
        模拟滑动操作
        """
        os.system('adb shell input swipe {} {} {} {}'.format(x, y, x2, y2))
