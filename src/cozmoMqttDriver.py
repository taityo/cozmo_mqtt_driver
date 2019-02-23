import cozmo
import paho.mqtt.client as mqtt
import time
import json

class CozmoDriver:

  def __init__(self, robot, host='localhost', port=1883):

    self.robot = robot
    self.host = host
    self.port = port

    #### Subscriber
    self.lift_sub = mqtt.Client()
    
    # callback function
    self.lift_sub.on_connect = self.on_connect_lift
    self.lift_sub.on_message = self.on_message_lift


    #### Publisher
    self.lift_pub = mqtt.Client() 


  def run(self):
    ### Subscriber

    # connection
    self.lift_sub.connect_async(self.host, self.port, keepalive=60)
    
    # loop_start
    self.lift_sub.loop_start()


    ### Publisher

    # connection
    self.lift_pub.connect_async(self.host, self.port, keepalive=60)
    
    # loop_start
    self.lift_pub.loop_start()


    ### run
    while True:
      self.publish_lift()

      time.sleep(0.05)


  ### Subscriber Callback Function

  def on_connect_lift(self, client, userdate, flags, respons_code):
    self.lift_sub.subscribe('/move_lift')
    print('Connected lift_sub !!')

  def on_message_lift(self, client, userdata, msg):
    print('Subscribed lift_sub !!')

    move_lift = json.loads(msg.payload)
    self.robot.move_lift(move_lift['speed'])
    print(move_lift)


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


import asyncio
import cozmo

async def cozmo_program(robot: cozmo.robot.Robot):
  coz = CozmoDriver(robot)
  coz.run()

if __name__ == '__main__':
  cozmo.run_program(cozmo_program)
  
