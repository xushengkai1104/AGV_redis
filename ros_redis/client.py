#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import redis
import time
import socket
import re

print('*** client start to work')

# 外网host名
host = 'r-uf6egwjn6dskz5of2fpd.redis.rds.aliyuncs.com'
# 端口号
port = 6379

print('*** hostname is '+host)
print('*** port is %d' %(port))

# 错误列表
error_dict = {
   u'非法指令':'Command is invalid',
   u'哈希表不存在':'ControlCom not exist'
   }

class client:

   def __init__(self):
      # 版本为python 2.7,键盘输入使用raw_input，单纯的input为指令输入
      password = raw_input('*** Enter password:')

      #用db来分别Agv的编号。
      self.r = redis.StrictRedis(host=host, port=port, db=0, password=password)
      
      # timeout 1s
      time.sleep(1)

   def redis_info(self):
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

      # 获取服务器当前时间
      print('*** Start_time is： ' +time.asctime(time.localtime(time.time())))
      
      im = 1
      #暂时设置 im 取代rospy.is_shutdown()
      while im == 1:
         time_now = time.asctime(time.localtime(time.time()))
         currentState = self.r.get('Status')
         print('*** AGV_state is : '+currentState)

         # 当AGV运行状态为运行中：
         if currentState == 'EXECUTING':
            if self.r.hexists('ControlCom','point1') == True:
               point1 = self.r.hget('ControlCom','point1')
               point2 = self.r.hget('ControlCom','point2')
               operate = self.r.hget('ControlCom','operate')
               print(point1,point2,operate)
               self.r.hset('agv_info','error','')
            else:
               # 判断与上一条错误消息是否相同，若相同则不添加
               error_info = self.r.hget('agv_info','error')
               if re.search(error_dict[u'哈希表不存在'],error_info) == None:
                  self.r.hset('agv_info','error',time_now + ': '+error_dict[u'哈希表不存在'])
         
         # 当AGV运行状态为空闲：
         elif currentState == 'IDLE':
            self.r.hset('agv_info','error','')
            
         # 当指令不合法时：
         else:
            error_info = self.r.hget('agv_info','error')
            if re.search(error_dict[u'非法指令'],error_info) == None:
               self.r.hset('agv_info','error',time_now + ': '+error_dict[u'非法指令'])

# 初始化client类
t = client()
t.redis_info()
