# -*- coding: utf-8 -*-

import os
import time
import re
from PIL import Image
import json
from threading import Thread


#封装 执行adb
def adb_exe(cmd,sleep=2):
	def wrapper(cmd,sleep):
		os.system(cmd)
		time.sleep(sleep)
	wrapper(cmd,sleep)

#获得链接的手机
class Device():

	#添加好友的btn 颜色
	addBtnColor = (26 , 173 , 25 , 255)

	def __init__(self,s):
		self.s = s
		(self.alpha,self.width,self.height,self.dpiNum) = self.adb_metric()


	#测试手机dpi = 240dpi
	#获得屏幕尺寸 / 像素密度
	def adb_metric(self):
		ret = os.popen('adb -s %s shell dumpsys window displays' % self.s)
		text = ret.read()
		dpi = re.search(r'(\d+)dpi',text)
		dpiNum = int(dpi.group(1))
		alpha = dpiNum / 240
		params = re.search('init=(\d+)x(\d+)',text)
		width = int(params.group(1))
		height = int(params.group(2))
		return (alpha ,width ,height ,dpiNum)
			
	
	#封装点击
	def adb_tap(self,x,y):
		adb_exe('adb -s %s shell input tap %s %s' % (self.s, x , y))
		
	
	#封装输入
	def adb_input(self,text):
		adb_exe('adb -s %s shell am broadcast -a ADB_INPUT_TEXT --es msg "%s"' % (self.s,text)) 
	
	
	#封装swipe
	def adb_swipe(self,y0,y1):
		adb_exe('adb -s %s shell input swipe 240 %s 240 %s ' % (self.s, y0 ,y1))
	
	
	def simu_loc(self,lat,long):
		''' 使用天下游模拟位置信息 '''
		#打开天下游
		adb_exe('adb -s %s shell am start com.txy.anywhere/com.txy.anywhere.activity.SplashActivity' % self.s)
		#点击输入经纬度信息
		self.adb_tap(440 * self.alpha , 410 * self.alpha)
		#点击输入经度edittext
		self.adb_tap(240 * self.alpha , 384 * self.alpha)
		#输入经度
		self.adb_input(long)
		#点击纬度
		self.adb_tap(240 * self.alpha , 468 * self.alpha)
		#输入纬度
		self.adb_input(lat)
		#确定
		self.adb_tap(360 * self.alpha, 552 * self.alpha)
		#开始模拟
		self.adb_tap(240 * self.alpha,305 * self.alpha)
		#返回一次
		self.add_after()
	
	
	def simu_loc_after(self):
		''' 停止模拟 '''
		#打开天下游
		adb_exe('adb -s %s shell am start com.txy.anywhere/com.txy.anywhere.activity.SplashActivity' % self.s)
		adb_tap(240 * self.alpha,305 * self.alpha)
	
	
	def add_before(self):
		''' 进入微信添加好友界面 '''
		adb_exe('adb -s %s shell am start com.tencent.mm/com.tencent.mm.ui.LauncherUI' % self.s)
		#发现
		self.adb_tap(300 * self.alpha , 814 * self.alpha)
		#附近的人
		self.adb_tap(240 * self.alpha,622 * self.alpha)
		#多等几秒
		time.sleep(5)
	
	
	def add(self,y):
		''' 添加好友 '''
		self.adb_tap(240 * self.alpha,y * self.alpha)
		self.adb_tap(240 * self.alpha,self.get_add_btn_pos())
		self.adb_input('您好,很希望认识您!')
		self.adb_tap(440 * self.alpha , 74 * self.alpha)
	
	
	def get_add_btn_pos(self):
		''' 获得打招呼按钮的btn '''
		adb_exe('adb -s %s shell screencap -p /sdcard/tmp%s.png' % (self.s,self.s))
		adb_exe('adb -s %s pull /sdcard/tmp%s.png' % (self.s, self.s))
		img = Image.open('tmp%s.png' % self.s)
		for y in range(1,self.height):
			if self.addBtnColor == img.getpixel((240,self.height - y)):
				return self.height -y
	
	
	def add_after(self):
		''' 添加完成之后 返回 '''
		time.sleep(1)
		adb_exe('adb -s %s shell input keyevent 4' % self.s) 
	
	
	def add_first_one(self):
		''' 添加第一个 '''
		self.add(157.5 * self.alpha)
		self.add_after()
	
	
	def scroll_to_next(self):
		self.adb_swipe(592 * self.alpha, 500 * self.alpha)


	def exe_all(self):
		#输入经纬度信息
		f = open('./position.json','rb')
		l = json.load(f);
		for i in l:
			#打开模拟
			self.simu_loc(i['lat'],i['long'])
			#进入添加好友
			self.add_before()
			#添加好友
			for _ in range(10):
				self.add_first_one()
				self.scroll_to_next()
			#返回微信主界面
			self.add_after()
			#停止模拟位置
			self.simu_loc_after()


if __name__ == '__main__':
	ret = os.popen('adb devices')
	text = ret.read()
	print(text)
	s = re.findall('\w+',text)
	devices = s[4::2]
	for s in devices:
		device = Device(s)
		thread = Thread(target=device.exe_all,args=())
		thread.start()

