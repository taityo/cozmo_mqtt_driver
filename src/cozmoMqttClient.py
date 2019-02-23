import json
import time

import paho.mqtt.client as mqtt


class CozmoClient:
  def __init__(self, host='localhost', port=1883):
    # instance valiable
    self.host = host
    self.port = port

    # callback valiable
    self.callback_lift = None

    ### Subscriber
    self.lift_sub = mqtt.Client()
   
    # callback function
    self.lift_sub.on_connect = self.on_connect_lift
    self.lift_sub.on_message = self.on_message_lift

    ### Publisher
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


  ### Subscriber Callback Function

  def on_connect_lift(self, client, userdate, flags, respons_code):
    self.lift_sub.subscribe('/lift_pos')
    print('Connected lift_sub !!')

  def on_message_lift(self, client, userdata, msg):
    print('Subscribed lift_sub !!')

    lift_pos = json.loads(msg.payload)
    if self.callback_lift != None:
      self.callback_lift(lift_pos)


  ### Publisher Function
 
  def publish_move_lift(self, speed):
    
    move_lift = {
      'speed': speed
    }
    
    # dict -> str on json & publish
    self.lift_pub.publish('/move_lift', json.dumps(move_lift))
    print('Publish lift_pub')


num = 1
i = 0

def func(lift_pos):
  global num

  if lift_pos['ratio'] >= 0.97:
    num = -1
  elif lift_pos['ratio'] <= 0.03:
    num = 1

  print(lift_pos)
    

if __name__ == '__main__':

  cozmo_client = CozmoClient()
  
  # callback function
  cozmo_client.callback_lift = func


  cozmo_client.run()
  while True:
    cozmo_client.publish_move_lift(i)
    i = i + num
    print('i :' + str(i))

    time.sleep(0.05)



