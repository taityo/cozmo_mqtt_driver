import time
import json
import base64

import cozmo
import paho.mqtt.client as mqtt
import numpy as np

from PIL import Image
from cozmo.util import Pose

class CozmoDriver:

  def __init__(self, robot, host='localhost', port=1883):

    self.robot = robot
    self.host = host
    self.port = port
    self.saying_now = None
    self.cmd_vel = None
    self.wheel = None
    self.last_pose = self.robot.pose
  
    # robot config
    self.robot.camera.image_stream_enabled = True
    self.robot.camera.color_image_enabled = True
    time.sleep(1) # 消すかも

    #### Subscriber

    # lift subscriber
    self.lift_sub = mqtt.Client()
    self.lift_sub.on_connect = self.on_connect_lift
    self.lift_sub.on_message = self.on_message_lift

    # head subscriber
    self.head_sub = mqtt.Client()
    self.head_sub.on_connect = self.on_connect_head
    self.head_sub.on_message = self.on_message_head

    # say_text subscriber
    self.saytext_sub = mqtt.Client()
    self.saytext_sub.on_connect = self.on_connect_saytext
    self.saytext_sub.on_message = self.on_message_saytext

    # cmd_vel subscriber
    self.cmd_vel_sub = mqtt.Client()
    self.cmd_vel_sub.on_connect = self.on_connect_cmd_vel
    self.cmd_vel_sub.on_message = self.on_message_cmd_vel


    #### Publisher

    self.lift_pub = mqtt.Client() # lift publisher
    self.head_pub = mqtt.Client() # head publisher
    self.saytext_pub = mqtt.Client() # saytext publisher
    self.camera_pub = mqtt.Client() # camera publisher
    self.odom_pub = mqtt.Client() # odom publisher


  def run(self, update_rate):
    ### Subscriber

    # lift subscriber
    self.lift_sub.connect_async(self.host, self.port, keepalive=60)
    self.lift_sub.loop_start()

    # head subscriber
    self.head_sub.connect_async(self.host, self.port, keepalive=60)
    self.head_sub.loop_start()

    # say_text subscriber
    self.saytext_sub.connect_async(self.host, self.port, keepalive=60)
    self.saytext_sub.loop_start()

    # cmd_vel subscriber
    self.cmd_vel_sub.connect_async(self.host, self.port, keepalive=60)
    self.cmd_vel_sub.loop_start()


    ### Publisher

    # lift publisher
    self.lift_pub.connect_async(self.host, self.port, keepalive=60)
    self.lift_pub.loop_start()

    # head publisher
    self.head_pub.connect_async(self.host, self.port, keepalive=60)
    self.head_pub.loop_start()

    # saytext publisher
    self.saytext_pub.connect_async(self.host, self.port, keepalive=60)
    self.saytext_pub.loop_start()

    # camera publisher
    self.camera_pub.connect_async(self.host, self.port, keepalive=60)
    self.camera_pub.loop_start()

    # odom publisher
    self.odom_pub.connect_async(self.host, self.port, keepalive=60)
    self.odom_pub.loop_start()

    ### run
    while True:
      self.publish_lift() # lift publish
      self.publish_head() # head publish
      self.publish_say_text() # say_text publish
      self.publish_camera() # camera publish
      self.publish_odom(update_rate) # odom publish

      if self.wheel != None:
        self.robot.drive_wheels(self.wheel['lv'], self.wheel['rv'])

      time.sleep(1.0/update_rate)


  ### Subscriber Callback Function

  # lift function
  def on_connect_lift(self, client, userdate, flags, respons_code):
    self.lift_sub.subscribe('/move_lift')
    print('Connected lift_sub !!')

  def on_message_lift(self, client, userdata, msg):
    print('Subscribed lift_sub !!')

    move_lift = json.loads(msg.payload)
    self.robot.move_lift(move_lift['speed'])

  # head function
  def on_connect_head(self, client, userdate, flags, respons_code):
    self.head_sub.subscribe('/move_head')
    print('Connected head_sub !!')

  def on_message_head(self, client, userdata, msg):
    print('Subscribed head_sub !!')

    move_head = json.loads(msg.payload)
    self.robot.move_head(move_head['speed'])
    #print(move_head)

  # saytext function
  def on_connect_saytext(self, client, userdate, flags, respons_code):
    self.saytext_sub.subscribe('/say_text')
    print('Connected saytext_sub !!')

  def on_message_saytext(self, client, userdata, msg):
    print('Subscribed saytext_sub !!')

    say_text = json.loads(msg.payload)
    self.robot.set_robot_volume(say_text['volume'])
    self.saying_now = self.robot.say_text(say_text['text'])

  # cmd_vel function
  def on_connect_cmd_vel(self, client, userdate, flags, respons_code):
    self.cmd_vel_sub.subscribe('/cmd_vel')
    print('Connected cmd_vel_sub !!')

  def on_message_cmd_vel(self, client, userdata, msg):
    print('Subscribed cmd_vel_sub !!')

    cmd_vel = json.loads(msg.payload)
    print(cmd_vel)

    axle_length = 0.07  # 7cm
    self.cmd_vel = cmd_vel
    linear = cmd_vel['linear']['x']
    angular = cmd_vel['angular']['z']
    rv = linear + (angular * axle_length * 0.5)
    lv = linear - (angular * axle_length * 0.5)

    # convert to mm / s
    self.wheel = {'lv': lv*1000, 'rv': rv*1000}


  ### Publisher Function

  def publish_lift(self):
    pos = self.robot.lift_position

    lift_pos = {
      'angle': pos.angle.radians,
      'height': pos.height.distance_mm,
      'ratio': pos.ratio
    }

    # dict -> str on json & publish
    self.lift_pub.publish('/lift_pos', json.dumps(lift_pos))
    print('Publish lift_pub !!')

  def publish_head(self):

    head_angle = {
      'angle': self.robot.head_angle.radians
    }

    # dict -> str on json & publish
    self.head_pub.publish('/head_angle', json.dumps(head_angle))
    print('Publish head_angle !!')

  def publish_say_text(self):

    say_text = {
      'saying_now': False
    }

    if self.saying_now != None:
      saying_now = self.saying_now.state == "action_running"
      say_text['saying_now'] = saying_now

    # dict -> str on json & publish
    self.saytext_pub.publish('/saying_now', json.dumps(say_text))
    print('Publish say_text !!')

  def publish_camera(self):

    ### image encode
    pil_img = self.robot.world.latest_image.raw_image
    # pil -> bainary
    bainary_img = pil_img.tobytes()
    # bainary -> base64
    bai2b64_img = base64.b64encode(bainary_img)
    # base64(bytes) -> str
    raw_image = bai2b64_img.decode('utf-8')

    camera_image = {
      'raw_image': raw_image
    }

    # dict -> str on json & publish
    self.camera_pub.publish('/camera_image', json.dumps(camera_image))
    print('Publish camera !!')

  def publish_odom(self, update_rate):
    
    # set pose and orient
    pose = self.robot.pose.position
    orient = self.robot.pose_angle.radians
    linear = 0
    angular = 0

    if self.cmd_vel != None:
      # 現在の直進速度と回転速度を計算
      delta_pose = self.last_pose - self.robot.pose
      dist = np.sqrt(delta_pose.position.x**2
                     + delta_pose.position.y**2
                     + delta_pose.position.z**2) / 1000.0
    
      linear = dist * update_rate * np.sign(self.cmd_vel['linear']['x'])
      angular = -delta_pose.rotation.angle_z.radians * update_rate
      # 本当にpose.rotation？

    odom = {
      'timestamp': time.time(),
      'pose': {
        'position': {'x': pose.x, 'y': pose.y, 'z': pose.z},
        'orientation': {'x': 0, 'y': 0, 'z': orient}
      },
      'twist': {
        'linear': {'x': linear, 'y': 0, 'z': 0 },
        'angular': { 'x': 0, 'y': 0, 'z': angular}
      }
    }
     
    # dict -> str on json & publish
    self.odom_pub.publish('/odom', json.dumps(odom))
    print('Publish Odometry !!')
  
    self.last_pose = self.robot.pose


import asyncio
import cozmo

async def cozmo_program(robot: cozmo.robot.Robot):
  coz = CozmoDriver(robot)
  coz.run()

if __name__ == '__main__':
  cozmo.run_program(cozmo_program)

  
