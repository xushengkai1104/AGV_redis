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
      password = raw_input('*** Enter password:')

      #用db来分别Agv的编号。
      self.r = redis.StrictRedis(host=host, port=port, db=0, password=password)
      
      # timeout 1s
      time.sleep(1)
      
      info_dict = {
         # 位姿
         'position_x':'',
         'position_y':'',
         'ori_x':'',
         'ori_y':'',
         'ori_z':'',
         'ori_w':'',
         # 当前速度
         'vel_x':'',
         'ang_z':'',
         # agv错误码
         'error':''
            }
      self.r.hmset('agv_info', info_dict)
      
      im = 1
      #暂时设置 im 取代rospy.is_shutdown()
      while im == 1:
         currentState = self.r.get('Status')
         print('*** AGV_state is : '+currentState)

         # 当AGV运行状态为运行中：
         if currentState == 'EXECUTING':
            if self.r.hexists('ControlCom','point1') == True:
               point1 = self.r.hget('ControlCom','point1')
               point2 = self.r.hget('ControlCom','point2')
               operate = self.r.hget('ControlCom','operate')
               print(point1,point2,operate)
               #此条为过渡指令
               self.r.hset('agv_info','error','')
            else:
               self.r.hset('agv_info','error','Hashtable: ControlCom not exist')
         
         # 当AGV运行状态为空闲：
         elif currentState == 'IDLE':
            print('*** Now agv is idle,wait for the command')
         # 当指令错误时：
         else:
            self.r.hset('agv_info','error','Command is wrong')
         time.sleep(1)
         

# 初始化client类
t = client()
