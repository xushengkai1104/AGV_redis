#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import redis
import time
import socket

print('*** client start to work')

host = 'r-uf6egwjn6dskz5of2fpd.redis.rds.aliyuncs.com'
port = 6379
password = 'Liuqin930425'

#注意这里的str和Int的表达区别
print('*** hostname is '+host)
print('*** port is %d' %(port))

class client:

   def __init__(self):
      self.r = redis.StrictRedis(host=host, port=port, password=password)

#初始化client类
t = client()
time.sleep(5)
temp = t.r.get("QinQin")
print(temp)
