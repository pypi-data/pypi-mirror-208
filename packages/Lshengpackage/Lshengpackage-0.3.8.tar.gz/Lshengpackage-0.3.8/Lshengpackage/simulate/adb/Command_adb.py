# -*coding:utf-8 -*-
# !/usr/bin/env python

from PIL import ImageFile
from PIL import Image
import os


class command:
    def dev(self):
        # 查看当前链接设备
        com = os.system('adb devices')
        return com

    def log(self):
        # 查看日志
        com = os.system('adb logcat')
        return com
    
    def kill(self):
        # 结束adb服务
        com = os.system('adb kill-server')
        return com

    def star(self):
        # 开始adb服务
        com = os.system('adb start-server')
        return com

    def install(self, apk_name):
        # 安装软件
        com = os.system('adb install -r {}.apk'.format(apk_name))
        return com

    def uninstall(self, apk_name):
        # 卸载
        com = os.system('adb uninstall {}.apk'.format(apk_name))
        return com

    def up(self, file_name, path_phone):
        # 上传SDCard/../..手机端路径
        com = os.system('adb push {} {}'.format(file_name, path_phone))
        return com

    def down(self, file_name):
        # 下载
        com = os.system('adb uninstall {}'.format(file_name))
        return com

    def scr(self, path_pic_name):
        # 屏幕截图到手机根目录
        com = os.system('adb shell screencap -p /sdcard/{}.png'.format(path_pic_name))
        return com

    def video_scr(self, video_name):
        # 录屏，默认mp4格式
        com = os.system('adb shell screenrecord /sdcard/{}.mp4'.format(video_name))
        return com

    def cut_scr(self, path_pic_name, path):
        # 屏幕截图到本地
        # pic_name:屏幕截图生成地址+名称，默认为手机的根目录,默认的来
        # path为文件夹目录下
        self.scr(path_pic_name)
        com = os.system("adb pull /sdcard/{} {}{}.png".format(path_pic_name, path, path_pic_name))
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        return com

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
        return True

    def tap_work(self, x, y):
        """
        模拟点击操作
        """
        com = os.system('adb shell input tap {} {}'.format(x, y))
        return com

    def swip_work(self, x, y, x2, y2):
        """
        模拟滑动操作
        """
        com = os.system('adb shell input swipe {} {} {} {}'.format(x, y, x2, y2))
        return com
