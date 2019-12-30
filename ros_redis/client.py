#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import redis
import time
import re
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion, Twist, PoseWithCovarianceStamped,PointStamped,PoseStamped
from math import radians, pi
from move_base_msgs.msg import *
from actionlib_msgs.msg import *
import rospy
import threading

# ------------------------------常量区-----------------------------------------------
# 外网host名
host = 'r-uf6egwjn6dskz5of2fpd.redis.rds.aliyuncs.com'
# 端口号
port = 6379

# 错误列表
error_dict = {
   u'非法指令':'Command is invalid',
   u'哈希表不存在':'ControlCom not exist',
   u'点坐标非法':'Point is invalid'
   }

#每隔多少个周期获取一次速度及位姿消息
delay = 5
count = 0

target_ptr = '0000'
last_ptr = '0000'

info_dict = {
   # 位姿
      'x':'',
      'y':'',
      'qz':'',
      'qw':'',
   # 当前速度
      'vel_x':'',
      'ang_z':''
           }
#-------------------------------------------------------------------------------------

class client:

   def __init__(self):
#----------------------------------需要更改区域-------------------------------------------
      rospy.init_node('redis_node', anonymous = False)
      rospy.loginfo('hostname is '+host)
      rospy.loginfo('port is %d' %(port))
      password = raw_input('*** Enter password:')

      #用db来分别Agv的编号。
      self.r = redis.StrictRedis(host=host, port=port, db=0, password=password)
#----------------------------------------------------------------------------------------      
      # timeout 1s--
      time.sleep(1)

      #(作废)另起线程获取agv位姿及速度信息
      #thread1 = myThread(1,"thread-1",1)
      #thread1.start()
      

   def shutdown(self):
      rospy.loginfo( 'Stopping the robot... '+ time.asctime(time.localtime(time.time())))
      rospy.sleep(2)

   def cmd_velcallback(self, vel):
      global info_dict
      info_dict['vel_x'] = str(vel.linear.x)
      info_dict['ang_z'] = str(vel.angular.z)
   
   def current_pose_callback(self,pose):
      global info_dict
      info_dict['x'] = str(pose.position.x)
      info_dict['y'] = str(pose.position.y)
      info_dict['qz'] = str(pose.orientation.z)
      info_dict['qw'] = str(pose.orientation.w)

   def setGoal(self,goal_x,goal_y,goal_qz,goal_qw):
      move_base = actionlib.SimpleActionClient("move_base",MoveBaseAction)
      goal = MoveBaseGoal()
      goal.target_pose.header.frame_id = 'map'
      goal.target_pose.header.stamp = rospy.Time.now()
      goal.target_pose.pose.position.x = float(goal_x)
      goal.target_pose.pose.position.y = float(goal_y)
      goal.target_pose.pose.orientation.z = float(goal_qz)
      goal.target_pose.pose.orientation.w = float(goal_qw)
      move_base.send_goal(goal)

   def status_callback(self,msg):
      global target_ptr
      global last_ptr
      if msg.status.status == 1:
         rospy.loginfo("target accepted")
         self.r.set('target_ptr',target_ptr)
      elif msg.status.status == 3:
         rospy.loginfo("goal reached")
         if last_ptr != target_ptr:
            last_ptr = target_ptr
            self.r.set('last_ptr',last_ptr)
         else:
            pass
         

   def redis_info(self):

      if self.r.hexists('agv_info','x') == False:
         global info_dict
         self.r.hmset('agv_info', info_dict)
      self.r.set('error','')
      self.r.set('last_ptr','0000')
      self.r.set('target_ptr','0000')

      # 当ros关闭时，调用函数。
      rospy.on_shutdown(self.shutdown)

      rospy.loginfo('Start_time is ' +time.asctime(time.localtime(time.time())))
      
      goal_status_sub = rospy.Subscriber("move_base/result",MoveBaseActionResult,self.status_callback)
      rospy.Subscriber('/cmd_vel',Twist,self.cmd_velcallback)
      rospy.Subscriber('robot_pose',Pose,self.current_pose_callback)

      global count
      global delay
      global target_ptr
      global last_ptr

      while not rospy.is_shutdown():
         count = count + 1
         time_now = time.asctime(time.localtime(time.time()))
         currentState = self.r.get('Status')
         print('*** AGV_state : '+currentState)

         if count % delay == 0 :
            self.r.hmset('agv_info',info_dict)

         # 当AGV运行状态为运行中：
         if currentState == 'EXECUTING':
            if self.r.hexists('ControlCom','point1') == True:
               point1 = self.r.hget('ControlCom','point1')
               point2 = self.r.hget('ControlCom','point2')
               # 如果point1为0000，试着此时是调度系统没有来得及更新，执行第二个点。
               if point1 == '0000':
                  if point2 == '0000':
                     pass
                     #self.r.set('Status','IDLE')
                     #self.r.set('target_ptr','0000')
                  elif target_ptr != point2:
                     target_ptr = point2
                     ptr_list = self.r.hmget(point2,'x','y','qz','qw')
                     goal_x = ptr_list[0]
                     goal_y = ptr_list[1]
                     goal_qz = ptr_list[2]
                     goal_qw = ptr_list[3]
                     self.setGoal(goal_x,goal_y,goal_qz,goal_qw)
               elif target_ptr != point1 and last_ptr != point1:
                  target_ptr = point1
                  ptr_list = self.r.hmget(point1,'x','y','qz','qw')
                  goal_x = ptr_list[0]
                  goal_y = ptr_list[1]
                  goal_qz = ptr_list[2]
                  goal_qw = ptr_list[3]
                  self.setGoal(goal_x,goal_y,goal_qz,goal_qw)
               #这里需要默认point1和point2一定是不一样的.
               elif target_ptr != point2 and last_ptr != point2:
                  target_ptr = point2
                  ptr_list = self.r.hmget(point2,'x','y','qz','qw')
                  goal_x = ptr_list[0]
                  goal_y = ptr_list[1]
                  goal_qz = ptr_list[2]
                  goal_qw = ptr_list[3]
                  self.setGoal(goal_x,goal_y,goal_qz,goal_qw)
               else :
                  pass
                  
                  
               operate = self.r.hget('ControlCom','operate')
            else:
               # 判断与上一条错误消息是否相同，若相同则不添加
               error_info = self.r.hget('agv_info','error')
               if re.search(error_dict[u'哈希表不存在'],error_info) == None:
                  self.r.set('error',time_now + ': '+error_dict[u'哈希表不存在'])
         
         # 当AGV运行状态为空闲：
         elif currentState == 'IDLE':
            pass
            
         # 当指令不合法时：
         else:
            error_info = self.r.hget('agv_info','error')
            if re.search(error_dict[u'非法指令'],error_info) == None:
               self.r.set('error',time_now + ': '+error_dict[u'非法指令'])

#class myThread (threading.Thread):   #继承父类threading.Thread
   #def __init__(self,threadID,name,counter):
      #threading.Thread.__init__(self)
      #self.threadID = threadID
      #self.name = name
      #self.counter = counter

   #def run(self): #把要执行的代码写到run函数里面，线程在创建后会直接运行run函数
      #rospy.loginfo('thread get started')
      #while not rospy.is_shutdown():
         #time.sleep(delay)
         
      

# 初始化client类
t = client()
t.redis_info()
