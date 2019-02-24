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
    self.callback_head = None

    ### Subscriber
    self.lift_sub = mqtt.Client()
    self.head_sub = mqtt.Client()
   
    # callback function
    self.lift_sub.on_connect = self.on_connect_lift
    self.lift_sub.on_message = self.on_message_lift
    self.head_sub.on_connect = self.on_connect_head
    self.head_sub.on_message = self.on_message_head
    
    ### Publisher
    self.lift_pub = mqtt.Client()
    self.head_pub = mqtt.Client()

  def run(self):
    ### Subscriber
    
    # connection
    self.lift_sub.connect_async(self.host, self.port, keepalive=60)
    self.head_sub.connect_async(self.host, self.port, keepalive=60)

    # loop_start
    self.lift_sub.loop_start()
    self.head_sub.loop_start()
    

    ### Publisher

    # connection
    self.lift_pub.connect_async(self.host, self.port, keepalive=60)
    self.head_pub.connect_async(self.host, self.port, keepalive=60)

    # loop_start
    self.lift_pub.loop_start()
    self.head_pub.loop_start()


  ### Subscriber Callback Function

  def on_connect_lift(self, client, userdate, flags, respons_code):
    self.lift_sub.subscribe('/lift_pos')
    print('Connected lift_sub !!')

  def on_message_lift(self, client, userdata, msg):
    print('Subscribed lift_sub !!')

    lift_pos = json.loads(msg.payload)
    if self.callback_lift != None:
      self.callback_lift(lift_pos)

  def on_connect_head(self, client, userdate, flags, respons_code):
    self.head_sub.subscribe('/head_angle')
    print('Connected head_sub !!')

  def on_message_head(self, client, userdata, msg):
    print('Subscribed head_sub !!')

    head_angle = json.loads(msg.payload)
    if self.callback_head != None:
      self.callback_head(head_angle)


  ### Publisher Function
 
  def publish_move_lift(self, speed):
    
    move_lift = {
      'speed': speed
    }
    
    # dict -> str on json & publish
    self.lift_pub.publish('/move_lift', json.dumps(move_lift))
    print('Publish lift_pub')

  def publish_move_head(self, speed):
    
    move_head = {
      'speed': speed
    }
    
    # dict -> str on json & publish
    self.head_pub.publish('/move_head', json.dumps(move_head))
    print('Publish head_pub')


num = -1
i = 0

def func(p):

  print(p)
    

if __name__ == '__main__':

  cozmo_client = CozmoClient()
  
  # callback function
  cozmo_client.callback_lift = func
  cozmo_client.callback_head = func


  cozmo_client.run()
  while True:
    cozmo_client.publish_move_head(i)
    cozmo_client.publish_move_lift(i)
    i = i + num
    print('i :' + str(i))

    time.sleep(0.05)





