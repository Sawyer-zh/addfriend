	# -*- coding: utf-8 -*-

import os
import time
import re
from PIL import Image

#封装 执行adb 命令休息一秒钟
def adb_exe(cmd,sleep=1):
	def wrapper(cmd,sleep):
		os.system(cmd)
		time.sleep(sleep)
	wrapper(cmd,sleep)


#封装点击
def adb_tap(x,y):
	adb_exe('adb shell input tap %s %s' % (x , y))
	

#封装输入
def adb_input(text):
	adb_exe('adb shell am broadcast -a ADB_INPUT_TEXT --es msg "%s"' % text) 


#封装swipe
def adb_swipe(y0,y1):
	adb_exe('adb shell input swipe 240 %s 240 %s ' % (y0 ,y1))


#测试手机dpi = 240dpi
#获得屏幕尺寸 / 像素密度
ret = os.popen('adb shell dumpsys window displays')
text = ret.read()
dpi = re.search('(\d+)dpi',text)
dpiNum = int(dpi.group(1))
alpha = dpiNum / 240
params = re.search('init=(\d+)x(\d+)',text)
width = int(params.group(1))
height = int(params.group(2))

#添加好友的btn 颜色
addBtnColor = (26 , 173 , 25 , 255)


def simu_loc(lat,long):
	''' 使用天下游模拟位置信息 '''
	#打开天下游
	adb_exe('adb shell am start com.txy.anywhere/com.txy.anywhere.activity.SplashActivity')
	#点击输入经纬度信息
	adb_tap(440 * alpha , 410 * alpha)
	#点击输入经度edittext
	adb_tap(240 * alpha , 384 * alpha)
	#输入经度
	adb_input(long)
	#点击纬度
	adb_tap(240 * alpha , 468 * alpha)
	#输入纬度
	adb_input(lat)
	#确定
	adb_tap(360 * alpha, 552 * alpha)
	#开始模拟
	adb_tap(240 * alpha,305 * alpha)
	#返回一次
	adb_exe('adb shell input keyevent 4')


def simu_loc_after():
	''' 停止模拟 '''
	#打开天下游
	adb_exe('adb shell am start com.txy.anywhere/com.txy.anywhere.activity.SplashActivity')
	adb_tap(240 * alpha,305 * alpha)


def add_before():
	''' 进入微信添加好友界面 '''
	adb_exe('adb shell am start com.tencent.mm/com.tencent.mm.ui.LauncherUI')
	#发现
	adb_tap(300 * alpha , 814 * alpha)
	#附近的人
	adb_tap(240 * alpha,622 * alpha)
	#多等几秒
	time.sleep(5)


def add(y):
	''' 添加好友 '''
	adb_tap(240 * alpha,y * alpha)
	adb_tap(240 * alpha,get_add_btn_pos())
	adb_input('您好,很希望认识您!')
	adb_tap(440 * alpha , 74 * alpha)


def get_add_btn_pos():
	''' 获得打招呼按钮的btn '''
	adb_exe('adb shell screencap -p /sdcard/tmp.png')
	adb_exe('adb pull /sdcard/tmp.png')
	img = Image.open('tmp.png')
	for y in range(1,height):
		if addBtnColor == img.getpixel((240,height - y)):
			return height -y


def add_after():
	''' 添加完成之后 返回 '''
	time.sleep(1)
	adb_exe('adb shell input keyevent 4')


def add_first_one():
	''' 添加第一个 '''
	add(157.5 * alpha)
	add_after()


def scroll_to_next():
	adb_swipe(591 * alpha, 500 * alpha)


def main():
	''' 添加好友 '''
	#输入经纬度信息
	lat= input('请输入纬度 ... ')
	long = input('请输入经度 ... ')
	#打开模拟
	simu_loc(lat,long)
	#进入添加好友
	add_before()
	#添加好友
	for _ in range(100):
		add_first_one()
		scroll_to_next()
	simu_loc_after()


if __name__ == '__main__':
	main()
