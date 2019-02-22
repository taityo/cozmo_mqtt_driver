import cozmo
import paho.mqtt.client as mqtt
import time

class CozmoDriver:

  def __init__(self, robot, host='localhost', port=1883):

    self.robot = robot

    #### Subscriber
    self.lift_sub = mqtt.Client()
    
    # callback function
    self.lift_sub.on_connect = self.lift_on_connect
    self.lift_sub.on_message = self.lift_on_message

    # connection
    self.lift_sub.connect_async(host, port, keepalive=60)
    
    # loop_start
    self.lift_sub.loop_start()


    #### Publisher
    self.lift_pub = mqtt.Client() 

    # callback function
    self.lift_pub.on_publish = self.lift_on_publish

    # connection
    self.lift_pub.connect_async(host, port, keepalive=60)
    
    # loop_start
    self.lift_pub.loop_start()

  def run(self):
    while True:
      self.lift_pub.publish('/lift_pos', 'lift_pos_test')

      time.sleep(0.05)


  ### Subscriber Callback Function

  def lift_on_connect(self, client, userdate, flags, respons_code):
    self.lift_sub.subscribe('/move_lift')
    print('Connected lift_sub !!')

  def lift_on_message(self, client, userdata, msg):
    print('Subscribed lift_sub !!')


  ### Publisher Callback Function

  def lift_on_publish(self, client, userdata, msg):
    print('Publish lift_pub !!')



import asyncio
import cozmo

async def cozmo_program(robot: cozmo.robot.Robot):
  coz = CozmoDriver(robot)
  coz.run()

if __name__ == '__main__':
  cozmo.run_program(cozmo_program)
  
