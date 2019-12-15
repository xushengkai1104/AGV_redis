#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import redis
import time
import socket

print('*** client start to work')

# 外网host名
host = 'r-uf6egwjn6dskz5of2fpd.redis.rds.aliyuncs.com'
# 端口号
port = 6379

# 注意这里的str和Int的表达区别
print('*** hostname is '+host)
print('*** port is %d' %(port))

class client:

   def __init__(self):
      # 版本为python 2.7,键盘输入使用raw_input，单纯的input为指令输入
      password = raw_input('*** Enter cloud password:')
      self.r = redis.StrictRedis(host=host, port=port, password=password)
      time.sleep(1)
      response = self.r.get("QinQin")
      print(response)
      cmd_dict = {
            #当前AGV状态
            'status': '',
            #充电时的状态
            'recharge_state': '',
            #运行错误，此处应将错误信息保存至本地，并带时间戳
            'error': '',
            #设置当前坐标
            'init_pose': '',
            #设置目标点坐标×2
            'set_goal1': '',
            'set_goal2': '',
            #当前坐标
            'current_pose': '',
            #当前速度
            'vel_x':'',
            'ang_z':''
            }
      self.r.hmset('CmdState', cmd_dict)
      im = 1
      #暂时设置取代rospy.is_shutdown()
      while im == 1:
         currentState = self.r.hget('CmdState','status')
         print(currentState)
         time.sleep(1)
         

# 初始化client类
t = client()
