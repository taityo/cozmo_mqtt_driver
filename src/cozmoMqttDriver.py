import cozmo
import paho.mqtt.client as mqtt
import time
import json

class CozmoDriver:

  def __init__(self, robot, host='localhost', port=1883):

    self.robot = robot
    self.host = host
    self.port = port
    self.saying_now = None

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


    #### Publisher

    self.lift_pub = mqtt.Client() # lift publisher
    self.head_pub = mqtt.Client() # head publisher
    self.saytext_pub = mqtt.Client() # saytext publisher


  def run(self):
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

    ### run
    while True:
      self.publish_lift() # lift publish
      self.publish_head() # head publish
      self.publish_say_text() # say_text publish

      time.sleep(0.05)


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
    print(say_text)
    self.robot.set_robot_volume(say_text['volume'])
    self.saying_now = self.robot.say_text(say_text['text'])


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

    if self.saying_now != None:

      saying_now = self.saying_now.state == "action_running"
      say_text = {
        'saying_now': saying_now
      }

      # dict -> str on json & publish
      self.saytext_pub.publish('/saying_now', json.dumps(say_text))
    print('Publish say_text !!')


import asyncio
import cozmo

async def cozmo_program(robot: cozmo.robot.Robot):
  coz = CozmoDriver(robot)
  coz.run()

if __name__ == '__main__':
  cozmo.run_program(cozmo_program)
  
