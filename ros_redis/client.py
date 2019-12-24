#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import redis
import time
import re
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion, Twist, PoseWithCovarianceStamped
from math import radians, pi
import rospy

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
      # timeout 1s
      time.sleep(1)

   def shutdown(self):
      rospy.loginfo( 'Stopping the robot... '+ time.asctime(time.localtime(time.time())))
      rospy.sleep(2)

   def cmd_velcallback(self, vel):
      self.r.hset('agv_info','vel_x',str(vel.linear.x))
      self.r.hset('agv_info','ang_z',str(vel.angular.z))
   
   def current_pose_callback(self,pose):
      self.r.hset('agv_info','x',pose.position.x)
      self.r.hset('agv_info','y',pose.position.y)
      self.r.hset('agv_info','z',pose.position.z)
      self.r.hset('agv_info','qx',pose.orientation.x)
      self.r.hset('agv_info','qy',pose.orientation.y)
      self.r.hset('agv_info','qz',pose.orientation.z)
      self.r.hset('agv_info','qw',pose.orientation.w)

   def setGoal(self,goal_x,goal_y,goal_qz,goal_qw):
      move_base = actionlib.SimpleActionClient("move_base",self.MoveBaseAction)
      goal = MoveBaseGoal()
      goal.target_pose.header.frame_id = 'map'
      goal.target_pose.header.stamp = rospy.Time.now()
      goal.target_pose.pose.position.x = float(goal_x)
      goal.target_pose.pose.position.y = float(goal_y)
      goal.target_pose.pose.orientation.z = float(goal_qz)
      goal.target_pose.pose.orientation.w = float(goal_qw)
      move_base.send_goal(goal)

   def redis_info(self):
      info_dict = {
         # 位姿
         'x':'',
         'y':'',
         'z':'',
         'qx':'',
         'qy':'',
         'qz':'',
         'qw':'',
         # 当前速度
         'vel_x':'',
         'ang_z':'',
         # agv错误码
         'error':''
            }
      self.r.hmset('agv_info', info_dict)

      # 当ros关闭时，调用函数。
      rospy.on_shutdown(self.shutdown)

      # 获取服务器当前时间
      rospy.loginfo('Start_time is ' +time.asctime(time.localtime(time.time())))

      while not rospy.is_shutdown():
         time_now = time.asctime(time.localtime(time.time()))
         currentState = self.r.get('Status')
         print('*** AGV_state : '+currentState)

         rospy.Subscriber('/cmd_vel',Twist,self.cmd_velcallback)
         rospy.Subscriber('robot_pose',Pose,self.current_pose_callback)

         # 当AGV运行状态为运行中：
         if currentState == 'EXECUTING':
            if self.r.hexists('ControlCom','point1') == True:
               point1 = self.r.hget('ControlCom','point1')
               # 如果point1为0000，试着此时是调度系统没有来得及更新，执行第二个点。
               if point1 == '0000':
                  point2 = self.r.hget('ControlCom','point2')
                  if point2 == '0000':
                  #当点1,点2都为0000，此时为无指令，小车状态回到idle。速度降为零（不一定）
                     self.r.set('Status','IDLE')
                  else:
                     ptr_list = self.r.hmget(point2,'x','y','qz','qw')
                     goal_x = ptr_list[0]
                     goal_y = ptr_list[1]
                     goal_qz = ptr_list[2]
                     goal_qw = ptr_list[3]
                     self.setGoal(goal_x,goal_y,goal_qz,goal_qw)
               else:
                  ptr_list = self.r.hmget(point1,'x','y','qz','qw')
                  goal_x = ptr_list[0]
                  goal_y = ptr_list[1]
                  goal_qz = ptr_list[2]
                  goal_qw = ptr_list[3]
                  self.setGoal(goal_x,goal_y,goal_qz,goal_qw)
                  
               operate = self.r.hget('ControlCom','operate')
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
