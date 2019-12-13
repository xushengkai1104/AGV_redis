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
      response = t.r.get("QinQin")
      print(response)

   def cmd_dict()

# 初始化client类
t = client()
